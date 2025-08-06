import json
import pytest
from  src.analyze_lineage import analyze_lineage
def test_update_usage(tmp_path):
    ast = [
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
    index = {
        "proc_update": {"params": [], "calls": [], "tables": ["employees"]}
    }
    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))
    analyze_lineage(str(index_file), str(ast_file), str(output_file))
    with output_file.open() as f:
        result = json.load(f)
    assert result["employees"]["usage"]["proc_update"] == ["write"]

def test_delete_usage(tmp_path):
    ast = [
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
    index = {
        "proc_delete": {"params": [], "calls": [], "tables": ["employees"]}
    }
    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))
    analyze_lineage(str(index_file), str(ast_file), str(output_file))
    with output_file.open() as f:
        result = json.load(f)
    assert result["employees"]["usage"]["proc_delete"] == ["write"]

def test_multiple_procs_access_same_table(tmp_path):
    ast = [
        {
            "proc_name": "proc_a",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "SELECT", "query": "SELECT * FROM t1"}
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
    assert set(result["t1"]["usage"].keys()) == {"proc_a", "proc_b"}
    assert result["t1"]["usage"]["proc_a"] == ["read"]
    assert result["t1"]["usage"]["proc_b"] == ["write"]

def test_proc_reads_and_writes_same_table(tmp_path):
    ast = [
        {
            "proc_name": "proc_rw",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {"type": "SELECT", "query": "SELECT * FROM t2"},
                {"type": "UPDATE", "table": "t2", "set": {"col": "val"}}
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
    assert set(result["t2"]["usage"]["proc_rw"]) == {"read", "write"}

@pytest.fixture
def simple_ast():
    return [
        {
            "proc_name": "proc_test",
            "params": [],
            "return_type": "VOID",
            "variables": [],
            "statements": [
                {
                    "type": "SELECT",
                    "query": "SELECT * FROM employees",
                    "into_vars": []
                },
                {
                    "type": "INSERT_INTO",
                    "table": "log_table",
                    "columns": ["id"],
                    "values": ["1"]
                }
            ]
        }
    ]

@pytest.fixture
def simple_index():
    return {
        "proc_test": {
            "params": [],
            "calls": [],
            "tables": ["employees", "log_table"]
        }
    }

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
     index_file= tmp_path /"index.json"
     ast_file= tmp_path / "ast.json"
     output_file= tmp_path / "output.json"

     index_file.write_text(json.dumps(index))
     ast_file.write_text(json.dumps(ast))
     #run analyze lineage
     analyze_lineage(str(index_file), str(ast_file),str(output_file))
     with output_file.open() as f:
            result = json.load(f)

     assert result["proc_main"]["type"] == "procedure"
     assert result["proc_sub"]["type"] == "procedure"
     assert "proc_sub" in result["proc_main"]["calls"]




# Test to check if read and write happen properly
def test_read_and_write_usage(tmp_path, simple_index, simple_ast) :
    index_file= tmp_path / "index.json"
    ast_file= tmp_path / "ast.json"
    output_file= tmp_path/ "output.json"

    #write json input
    index_file.write_text(json.dumps(simple_index))
    ast_file.write_text(json.dumps(simple_ast))

    # run the tests to analyze the lineage 
    analyze_lineage(str(index_file), str(ast_file), str(output_file))

    # Load and assert output
    with output_file.open() as f:
        result = json.load(f)
    
    #run the assertion tests
    assert result["employees"]["type"]=="table"
    assert "proc_test" in result["employees"]["calls"]
    assert result["employees"]["usage"]["proc_test"] == ["read"]

    assert result["log_table"]["type"] == "table"
    assert "proc_test" in result["log_table"]["calls"]
    assert result["log_table"]["usage"]["proc_test"] == ["write"]

    assert result["proc_test"]["type"] == "procedure"

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
    assert result["table1"]["usage"]["proc_a"] == ["read"]

    # table2: written by proc_a (INSERT) and updated by proc_b (UPDATE)
    assert sorted(result["table2"]["usage"]["proc_a"]) == ["write"]
    assert sorted(result["table2"]["usage"]["proc_b"]) == ["write"]

    # table3: deleted by proc_b
    assert result["table3"]["usage"]["proc_b"] == ["write"]

    # Ensure both procedures are listed
    assert result["proc_a"]["type"] == "procedure"
    assert result["proc_b"]["type"] == "procedure"


#test complex sql query with some scope for RAW_SQL
# NOTE- IF THIS TEST FAILS THEN ITS HIGLY LIKELY THAT THE ISSUE IS DUE TO THE CHANGED AST STRUCTURE. PLEASE VERIFY THE AST STRUCTURE BELOW AGAINST THE FIELDS THE CODE IS EXPECTING

def test_RAW_SQL_and_complex_queries(tmp_path):
    index_file = tmp_path / "index.json"
    ast_file = tmp_path / "ast.json"
    output_file = tmp_path / "output.json"

    index_data={
  "AcmeERP.usp_ProcessFullPayrollCycle": {
    "params": [
      {
        "name": "@PayPeriodStart",
        "type": "DATE"
      },
      {
        "name": "@PayPeriodEnd",
        "type": "DATE"
      }
    ],
    "calls": [],
    "tables": [
      "AcmeERP.PayrollLogs",
      "AcmeERP.ExchangeRates",
      "#PayrollCalc"
    ]
  }
}
    
    ast_data=[
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
]
    index_file.write_text(json.dumps(index_data))
    ast_file.write_text(json.dumps(ast_data))

    analyze_lineage(str(index_file), str(ast_file), str(output_file))
    with open(output_file)as f:
        result=json.load(f)
    
    #important assertions
    assert result["AcmeERP.usp_ProcessFullPayrollCycle"]["type"]=="procedure"
    assert result["AcmeERP.PayrollLogs"]["type"]=="table"
    #if the AST structure doesnt handle NESTED queries properly then this testcase if passed shows that RAW_SQL and all other query_fields are also getting scanned by the lineage analyzer
    assert result["AcmeERP.PayrollLogs"]["usage"]["AcmeERP.usp_ProcessFullPayrollCycle"]==["write"]
    #proc calling table
    assert result["AcmeERP.Employees"]["calls"]==["AcmeERP.usp_ProcessFullPayrollCycle"]
    assert result["AcmeERP.Employees"]["usage"]["AcmeERP.usp_ProcessFullPayrollCycle"]==["read"]

    