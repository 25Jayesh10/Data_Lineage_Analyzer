import json
import pytest
from  src.analyze_lineage import analyze_lineage
def test_update_and_delete_usage(tmp_path):
    # --- UPDATE test setup ---
    ast_update = [
        {
            "proc_name": "proc_update",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "UPDATE", "table": "employees", "set": {"salary": "salary+1000"}}
            ]
        }
    ]
    index_update = {
        "proc_update": {"params": [], "calls": [], "tables": ["employees"]}
    }

    # --- DELETE test setup ---
    ast_delete = [
        {
            "proc_name": "proc_delete",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "DELETE", "table": "employees"}
            ]
        }
    ]
    index_delete = {
        "proc_delete": {"params": [], "calls": [], "tables": ["employees"]}
    }

    # Helper to run and load result
    def run_case(ast, index):
        index_file = tmp_path / "index.json"
        ast_file = tmp_path / "ast.json"
        output_file = tmp_path / "output.json"
        index_file.write_text(json.dumps(index))
        ast_file.write_text(json.dumps(ast))
        analyze_lineage(str(index_file), str(ast_file), str(output_file))
        with output_file.open() as f:
            return json.load(f)

    # --- Run UPDATE case ---
    result_update = run_case(ast_update, index_update)
    assert "employees" in result_update
    assert result_update["employees"]["type"] == "table"
    assert {
        "name": "salary",
        "usage": "write",
        "calling_procedure": "proc_update"
    } in result_update["employees"]["columns"]
    assert "DUMMY_TABLE" not in result_update
    assert "NO_TABLE" not in result_update

    # --- Run DELETE case ---
    result_delete = run_case(ast_delete, index_delete)
    assert "employees" in result_delete
    assert result_delete["employees"]["type"] == "table"
    assert "proc_delete" in result_delete["employees"]["calls"]
    assert {
        "name": "*",
        "usage": "write",
        "calling_procedure": "proc_delete"
    } in result_delete["employees"]["columns"]
    assert "DUMMY_TABLE" not in result_delete
    assert "NO_TABLE" not in result_delete


def test_multiple_procs_access_same_table(tmp_path):
    ast = [
        {
            "proc_name": "proc_a",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "SELECT", "query": "SELECT col1, col2 FROM t1"}
            ]
        },
        {
            "proc_name": "proc_b",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "UPDATE", "table": "t1", "set": {"col": "val"}}
            ]
        }
    ]
    index = {
        "proc_a": {"params": [], "calls": [], "tables": ["t1"]},
        "proc_b": {"params": [], "calls": [], "tables": ["t1"]}
    }

    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))

    analyze_lineage(str(index_file), str(ast_file), str(output_file))

    with output_file.open() as f:
        result = json.load(f)

    # Ensure table exists and is a table type
    assert "t1" in result
    assert result["t1"]["type"] == "table"

    # Extract all (col_name, usage, proc) triples for t1
    col_entries = result["t1"]["columns"]

    # Check that proc_a has read usage for its columns
    for col in col_entries:
      if col["calling_procedure"]=="proc_a":
        assert col["usage"] == "read" 
      if col["calling_procedure"]=="proc_b":
        assert col["usage"] == "write" 
     
        
    

    

    # Ensure no dummy or no_table entries
    assert "DUMMY_TABLE" not in result
    assert "NO_TABLE" not in result


def test_proc_reads_and_writes_same_table(tmp_path):
    ast = [
        {
            "proc_name": "proc_rw",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "SELECT", "query": "SELECT col1 FROM t2"},
                {"type": "UPDATE", "table": "t2", "set": {"col2": "val"}}
            ]
        }
    ]
    index = {
        "proc_rw": {"params": [], "calls": [], "tables": ["t2"]}
    }

    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))

    analyze_lineage(str(index_file), str(ast_file), str(output_file))

    with output_file.open() as f:
        result = json.load(f)

    # Ensure table exists
    assert "t2" in result
    assert result["t2"]["type"] == "table"

    col_entries = result["t2"]["columns"]

    # Ensure there is at least one read and one write usage from proc_rw
    for col in col_entries:
        assert (col["usage"]=="read" and col["calling_procedure"]=="proc_rw") or (col["usage"]=="write" and col["calling_procedure"]=="proc_rw")

    # Ensure no dummy/no_table entries
    assert "DUMMY_TABLE" not in result
    assert "NO_TABLE" not in result

# Test to check if one procedure calls another

def test_procedure_calls_another(tmp_path):
    ast = [
        {
            "proc_name": "proc_main",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "EXECUTE_PROCEDURE", "procedure": "proc_sub", "args": []}
            ]
        },
        {
            "proc_name": "proc_sub",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": []
        }
    ]
    index = {
        "proc_main": {"params": [], "calls": ["proc_sub"], "tables": []},
        "proc_sub": {"params": [], "calls": [], "tables": []}
    }

    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"

    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))

    # Run analyzer
    analyze_lineage(str(index_file), str(ast_file), str(output_file))

    with output_file.open() as f:
        result = json.load(f)

    # Ensure both procs exist and are typed correctly
    assert "proc_main" in result
    assert "proc_sub" in result
    assert result["proc_main"]["type"] == "procedure"
    assert result["proc_sub"]["type"] == "procedure"

    # Ensure proc_main calls proc_sub
    assert "proc_sub" in result["proc_main"]["calls"]

    # Ensure no unexpected DUMMY_TABLE / NO_TABLE
    assert "DUMMY_TABLE" not in result
    assert "NO_TABLE" not in result






#when multiple procedures are present in the input 
def test_multiple_procedures_lineage(tmp_path):
    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"

    # Simulated Index for multiple procedures
    index_data = {
        "proc_a": {
            "params": [],
            "calls": [],
            "tables": ["table1", "table2"]
        },
        "proc_b": {
            "params": [],
            "calls": [],
            "tables": ["table2", "table3"]
        }
    }

    # Simulated AST for multiple procedures
    ast_data = [
        {
            "proc_name": "proc_a",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {
                    "type": "SELECT_INTO",
                    "query": "SELECT * FROM table1",
                    "into_vars": []
                },
                {
                    "type": "INSERT_INTO",
                    "table": "table2",
                    "columns": ["id"],
                    "values": ["1"]
                }
            ]
        },
        {
            "proc_name": "proc_b",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {
                    "type": "UPDATE",
                    "table": "table2",
                    "set": {"name": "'newname'"}
                },
                {
                    "type": "DELETE",
                    "table": "table3",
                    "where": "id = 1"
                }
            ]
        }
    ]

    # Write input files
    index_file.write_text(json.dumps(index_data))
    ast_file.write_text(json.dumps(ast_data))

    # Call the lineage analyzer
    analyze_lineage(str(index_file), str(ast_file), str(output_file))

    # Validate output
    with open(output_file) as f:
        result = json.load(f)

    # table1: read by proc_a
    assert {
        "name": "*",
        "usage": "read",
        "calling_procedure": "proc_a"
    } in result["table1"]["columns"]

    # table2: written by proc_a (INSERT) and updated by proc_b (UPDATE)
    assert {
        "name": "id",
        "usage": "write",
        "calling_procedure": "proc_a"
    } in result["table2"]["columns"]
    assert {
        "name": "name",
        "usage": "write",
        "calling_procedure": "proc_b"
    } in result["table2"]["columns"]

    # table3: deleted by proc_b
    assert {
        "name": "*",
        "usage": "write",
        "calling_procedure": "proc_b"
    } in result["table3"]["columns"]

    # Ensure both procedures are listed
    assert result["proc_a"]["type"] == "procedure"
    assert result["proc_b"]["type"] == "procedure"


#test complex sql query with some scope for RAW_SQL
# NOTE- IF THIS TEST FAILS THEN ITS HIGLY LIKELY THAT THE ISSUE IS DUE TO THE CHANGED AST STRUCTURE. PLEASE VERIFY THE AST STRUCTURE BELOW AGAINST THE FIELDS THE CODE IS EXPECTING
def test_RAW_SQL_and_complex_queries(tmp_path):
    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"

    index_data = {
        "AcmeERP.usp_ProcessFullPayrollCycle": {
            "params": [
                {"name": "@PayPeriodStart", "type": "DATE"},
                {"name": "@PayPeriodEnd", "type": "DATE"}
            ],
            "calls": [],
            "tables": [
                "AcmeERP.PayrollLogs",
                "AcmeERP.ExchangeRates",
                "#PayrollCalc"
            ]
        }
    }

    ast_data =[
  {
    "proc_name": "AcmeERP.usp_ProcessFullPayrollCycle",
    "params": [
      {
        "name": "@PayPeriodStart",
        "type": "DATE",
        "mode": "IN"
      },
      {
        "name": "@PayPeriodEnd",
        "type": "DATE",
        "mode": "IN"
      }
    ],
    "return_type": "VOID",
    "variables": [
      { "name": "@EmployeeID", "type": "INT" },
      { "name": "@BaseSalary", "type": "DECIMAL" },
      { "name": "@Bonus", "type": "DECIMAL" },
      { "name": "@GrossSalary", "type": "DECIMAL" },
      { "name": "@Tax", "type": "DECIMAL" },
      { "name": "@NetSalary", "type": "DECIMAL" },
      { "name": "@Currency", "type": "CHAR" },
      { "name": "@ConvertedSalary", "type": "DECIMAL" },
      { "name": "@ExchangeRate", "type": "DECIMAL" },
      { "name": "@CurrentDate", "type": "DATE" },
      { "name": "@ErrorMsg", "type": "NVARCHAR" },
      { "name": "@ErrorSeverity", "type": "INT" },
      { "name": "@ErrorState", "type": "INT" }
    ],
    "statements": [
      {
        "type": "RAW_SQL",
        "query": "SET NOCOUNT ON;"
      },
      {
        "type": "TRY",
        "body": [
          { "type": "BEGIN_TRANSACTION" },
          {
            "type": "SET",
            "name": "@CurrentDate",
            "value": "GETDATE()"
          },
          {
            "type": "RAW_SQL",
            "query": "IF OBJECT_ID('tempdb..#PayrollCalc') IS NOT NULL DROP TABLE #PayrollCalc;"
          },
          {
            "type": "DECLARE_TEMP_TABLE",
            "name": "#PayrollCalc",
            "query": "CREATE TABLE #PayrollCalc (EmployeeID INT, BaseSalary DECIMAL(18,2), Bonus DECIMAL(18,2), GrossSalary DECIMAL(18,2), Tax DECIMAL(18,2), NetSalary DECIMAL(18,2), Currency CHAR(3), ConvertedSalary DECIMAL(18,2));"
          },
          {
            "type": "RAW_SQL",
            "query": "INSERT INTO #PayrollCalc (EmployeeID, BaseSalary, Bonus, GrossSalary, Tax, NetSalary, Currency) SELECT e.EmployeeID, e.BaseSalary, CASE WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 10 THEN e.BaseSalary * 0.15 WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 5 THEN e.BaseSalary * 0.10 WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 2 THEN e.BaseSalary * 0.05 ELSE 0 END AS Bonus, e.BaseSalary + CASE WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 10 THEN e.BaseSalary * 0.15 WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 5 THEN e.BaseSalary * 0.10 WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 2 THEN e.BaseSalary * 0.05 ELSE 0 END AS GrossSalary, CASE WHEN e.BaseSalary <= 50000 THEN e.BaseSalary * 0.1 WHEN e.BaseSalary <= 75000 THEN e.BaseSalary * 0.15 ELSE e.BaseSalary * 0.2 END AS Tax, (e.BaseSalary + CASE WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 10 THEN e.BaseSalary * 0.15 WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 5 THEN e.BaseSalary * 0.10 WHEN DATEDIFF(YEAR, e.HireDate, @PayPeriodEnd) >= 2 THEN e.BaseSalary * 0.05 ELSE 0 END) - CASE WHEN e.BaseSalary <= 50000 THEN e.BaseSalary * 0.1 WHEN e.BaseSalary <= 75000 THEN e.BaseSalary * 0.15 ELSE e.BaseSalary * 0.2 END AS NetSalary, ISNULL(e.Currency, 'USD') AS Currency FROM AcmeERP.Employees e;"
          },
          {
            "type": "DECLARE_CURSOR",
            "cursor_name": "PayrollCursor",
            "query": "SELECT EmployeeID, GrossSalary, Currency FROM #PayrollCalc"
          },
          { "type": "OPEN_CURSOR", "cursor_name": "PayrollCursor" },
          {
            "type": "FETCH_CURSOR",
            "cursor_name": "PayrollCursor",
            "fetch_into": ["@EmployeeID", "@GrossSalary", "@Currency"]
          },
          {
            "type": "WHILE",
            "condition": { "op": "=", "left": "@@FETCH_STATUS", "right": "0" },
            "body": [
              {
                "type": "IF",
                "condition": { "op": "<>", "left": "@Currency", "right": "'USD'" },
                "then": [
                  {
                    "type": "SELECT_INTO",
                    "query": "SELECT TOP 1 RateToBase FROM AcmeERP.ExchangeRates WHERE CurrencyCode = @Currency AND RateDate <= @CurrentDate ORDER BY RateDate DESC",
                    "into_vars": ["@ExchangeRate"]
                  },
                  {
                    "type": "IF",
                    "condition": { "op": "IS", "left": "@ExchangeRate", "right": "NULL" },
                    "then": [
                      { "type": "SET", "name": "@ExchangeRate", "value": "1" }
                    ]
                  },
                  {
                    "type": "SET",
                    "name": "@ConvertedSalary",
                    "value": { "op": "*", "left": "@GrossSalary", "right": "@ExchangeRate" }
                  }
                ],
                "else": [
                  { "type": "SET", "name": "@ConvertedSalary", "value": "@GrossSalary" }
                ]
              },
              {
                "type": "UPDATE",
                "table": "#PayrollCalc",
                "set": { "ConvertedSalary": "@ConvertedSalary" },
                "where": { "op": "=", "left": "EmployeeID", "right": "@EmployeeID" }
              },
              {
                "type": "FETCH_CURSOR",
                "cursor_name": "PayrollCursor",
                "fetch_into": ["@EmployeeID", "@GrossSalary", "@Currency"]
              }
            ]
          },
          { "type": "CLOSE_CURSOR", "cursor_name": "PayrollCursor" },
          { "type": "DEALLOCATE_CURSOR", "cursor_name": "PayrollCursor" },
          {
            "type": "RAW_SQL",
            "query": "INSERT INTO AcmeERP.PayrollLogs (EmployeeID, PayPeriodStart, PayPeriodEnd, GrossSalary, TaxDeducted) SELECT EmployeeID, @PayPeriodStart, @PayPeriodEnd, ConvertedSalary, Tax FROM #PayrollCalc;"
          },
          { "type": "COMMIT" }
        ],
        "catch": [
          {
            "exception": "ANY",
            "body": [
              {
                "type": "IF",
                "condition": { "op": ">", "left": "@@TRANCOUNT", "right": "0" },
                "then": [
                  { "type": "ROLLBACK" }
                ]
              },
              {
                "type": "RAW_SQL",
                "query": "SELECT @ErrorMsg = ERROR_MESSAGE(), @ErrorSeverity = ERROR_SEVERITY(), @ErrorState = ERROR_STATE();"
              },
              {
                "type": "RAISE",
                "message": "RAISERROR (@ErrorMsg, @ErrorSeverity, @ErrorState);"
              }
            ]
          }
        ]
      }
    ]
  }
]  # your existing AST JSON structure goes here exactly as in the original

    # Write files
    index_file.write_text(json.dumps(index_data))
    ast_file.write_text(json.dumps(ast_data))

    # Run analyzer
    analyze_lineage(str(index_file), str(ast_file), str(output_file))

    # Read output
    with output_file.open() as f:
        result = json.load(f)

    # Assertions for procedure type
    assert result["AcmeERP.usp_ProcessFullPayrollCycle"]["type"] == "procedure"

    # PayrollLogs table should be written to by the procedure
    assert result["AcmeERP.PayrollLogs"]["type"] == "table"
    assert {
        "name": "*",
        "usage": "write",
        "calling_procedure": "AcmeERP.usp_ProcessFullPayrollCycle"
    } in result["AcmeERP.PayrollLogs"]["columns"]

    # Employees table should be read by the procedure
    assert result["AcmeERP.Employees"]["type"] == "table"
    assert {
        "name": "*",
        "usage": "read",
        "calling_procedure": "AcmeERP.usp_ProcessFullPayrollCycle"
    } in result["AcmeERP.Employees"]["columns"]

    # Procedure should be recorded as calling the table
    assert "AcmeERP.usp_ProcessFullPayrollCycle" in result["AcmeERP.Employees"]["calls"]

    # Ensure no dummy or NO_TABLE entries exist
    assert "DUMMY_TABLE" not in result
    assert "NO_TABLE" not in result

 

def test_nested_ifs(tmp_path):
    # AST input
    ast = [
        {
            "proc_name": "Finance.usp_CheckAccountStatus",
            "params": [
                {"name": "@AccountID", "type": "INT", "mode": "IN"},
                {"name": "@MinBalance", "type": "DECIMAL", "mode": "IN"}
            ],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {
                    "type": "IF",
                    "condition": {
                        "type": "RAW_EXPRESSION",
                        "expression": "EXISTS (SELECT 1 FROM Finance.Accounts WHERE AccountID = @AccountID)"
                    },
                    "then": [
                        {
                            "type": "IF",
                            "condition": {
                                "op": ">=",
                                "left": {
                                    "type": "RAW_EXPRESSION",
                                    "expression": "(SELECT Balance FROM Finance.Accounts WHERE AccountID = @AccountID)"
                                },
                                "right": "@MinBalance"
                            },
                            "then": [
                                {
                                    "type": "SELECT",
                                    "columns": [
                                        "'Account is active and meets minimum balance' AS StatusMessage"
                                    ],
                                    "from": "DUMMY_TABLE"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    # Index input
    index = {
        "Finance.usp_CheckAccountStatus": {
            "params": [
                {"name": "@AccountID", "type": "INTEGER"},
                {"name": "@MinBalance", "type": "NUMERIC"}
            ],
            "calls": [],
            "tables": []
        }
    }

    # Write temp files
    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))

    # Run lineage analyzer
    analyze_lineage(str(index_file), str(ast_file), str(output_file))

    # Load results
    with output_file.open() as f:
        result = json.load(f)

    # ✅ Check procedure exists
    assert "Finance.usp_CheckAccountStatus" in result
    assert result["Finance.usp_CheckAccountStatus"]["type"] == "procedure"

    # ✅ Ensure FINANCE.ACCOUNTS is linked to the procedure
    assert "FINANCE.ACCOUNTS" in result["Finance.usp_CheckAccountStatus"]["tables"]

    # ✅ Ensure FINANCE.ACCOUNTS has the correct type and column names
    assert result["FINANCE.ACCOUNTS"]["type"] == "table"
    col_names = {col["name"] for col in result["FINANCE.ACCOUNTS"]["columns"]}
    assert "1" in col_names
    assert "Balance" in col_names

    # ✅ Ensure no dummy/no table entries are present
    forbidden_tables = {"DUMMY_TABLE", "NO_TABLE"}
    for table_name in result.keys():
        assert table_name not in forbidden_tables
    