import pytest
import json
from src.validation_script import validate

#testing when the ast and index are consistent as per the naive validation logic

def test_validate_consistent(tmp_path):
    ast=[
  {
    "proc_name": "Sales.usp_CalculateDiscount",
    "params": [
      { "name": "@CustomerID", "type": "INT", "mode": "IN" },
      { "name": "@OrderTotal", "type": "DECIMAL", "mode": "IN" }
    ],
    "return_type": "DECIMAL",
    "variables": [
      { "name": "@DiscountRate", "type": "DECIMAL" }
    ],
    "statements": [
      {
        "type": "IF",
        "condition": {
          "op": ">",
          "left": "@OrderTotal",
          "right": 1000
        },
        "then": [
          {
            "type": "SET",
            "name": "@DiscountRate",
            "value": 0.1
          }
        ],
        "else": [
          {
            "type": "SET",
            "name": "@DiscountRate",
            "value": 0.05
          }
        ]
      },
      {
        "type": "RETURN",
        "expression": "@DiscountRate"
      }
    ]
  },
  {
    "proc_name": "Sales.usp_UpdateOrderStatus",
    "params": [
      { "name": "@OrderID", "type": "INT", "mode": "IN" },
      { "name": "@NewStatus", "type": "VARCHAR", "mode": "IN" }
    ],
    "return_type": "INT",
    "variables": [],
    "statements": [
      {
        "type": "UPDATE",
        "table": "Orders",
        "set": {
          "Status": "@NewStatus"
        },
        "where": {
          "op": "=",
          "left": "ID",
          "right": "@OrderID"
        }
      },
      {
        "type": "RETURN",
        "expression": 1
      }
    ]
  }
    
]
    index={
  "Sales.usp_CalculateDiscount": {
    "params": [
      {
        "name": "@CustomerID",
        "type": "INTEGER"
      },
      {
        "name": "@OrderTotal",
        "type": "NUMERIC"
      }
    ],
    "calls": [],
    "tables": []
  },
  "Sales.usp_UpdateOrderStatus": {
    "params": [
      {
        "name": "@OrderID",
        "type": "INTEGER"
      },
      {
        "name": "@NewStatus",
        "type": "VARCHAR"
      }
    ],
    "calls": [],
    "tables": [
      "Orders"
    ]
  }
}
    index_file=tmp_path/"index.json"
    ast_file=tmp_path/"ast.json"
    
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))
    assert validate(index_file,ast_file) == True

#when case insensitivity is the issue
def test_validate_inconsistent_casing(tmp_path):
    """This will try to validate the two when there are casing issues between the data items (upercase,lowercase, mixed case key declarations)"""
    # proc name is fully lower case here
    ast=[
  {
    "proc_name": "sales.usp_calculatediscount",
    "params": [
      { "name": "@CustomerID", "type": "INT", "mode": "IN" },
      { "name": "@OrderTotal", "type": "DECIMAL", "mode": "IN" }
    ],
    "return_type": "DECIMAL",
    "variables": [
      { "name": "@DiscountRate", "type": "DECIMAL" }
    ],
    "statements": [
      {
        "type": "IF",
        "condition": {
          "op": ">",
          "left": "@OrderTotal",
          "right": 1000
        },
        "then": [
          {
            "type": "SET",
            "name": "@DiscountRate",
            "value": 0.1
          }
        ],
        "else": [
          {
            "type": "SET",
            "name": "@DiscountRate",
            "value": 0.05
          }
        ]
      },
      {
        "type": "RETURN",
        "expression": "@DiscountRate"
      }
    ]
  },
  {
    "proc_name": "Sales.usp_UpdateOrderStatus",
    "params": [
      { "name": "@OrderID", "type": "INT", "mode": "IN" },
      { "name": "@NewStatus", "type": "VARCHAR", "mode": "IN" }
    ],
    "return_type": "INT",
    "variables": [],
    "statements": [
      {
        "type": "UPDATE",
        "table": "Orders",
        "set": {
          "Status": "@NewStatus"
        },
        "where": {
          "op": "=",
          "left": "ID",
          "right": "@OrderID"
        }
      },
      {
        "type": "RETURN",
        "expression": 1
      }
    ]
  }
    
]
    index={
  "Sales.usp_CalculateDiscount": {
    "params": [
      {
        "name": "@CustomerID",
        "type": "INTEGER"
      },
      {
        "name": "@OrderTotal",
        "type": "NUMERIC"
      }
    ],
    "calls": [],
    "tables": []
  },
  "Sales.usp_UpdateOrderStatus": {
    "params": [
      {
        "name": "@OrderID",
        "type": "INTEGER"
      },
      {
        "name": "@NewStatus",
        "type": "VARCHAR"
      }
    ],
    "calls": [],
    "tables": [
      "Orders"
    ]
  }
}
    index_file=tmp_path/"index.json"
    ast_file=tmp_path/"ast.json"
    
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))
    assert validate(index_file,ast_file) == False

def test_validate_corrupted_file(tmp_path):
    """The 'proc_name' filed from the ast is missing here. This test is designed to check for that case"""
    ast = [
        {
            
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
    index_file=tmp_path/"index.json"
    ast_file=tmp_path/"ast.json"
    
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))
    assert validate(index_file,ast_file) == False

def test_validate_inconsistent_procedures(tmp_path):
    """The 'proc_name' filed from the ast is missing here. This test is designed to check for that case"""
    ast = [
        {
            "proc_name": "my_proc",
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
    index_file=tmp_path/"index.json"
    ast_file=tmp_path/"ast.json"
    
    index_file.write_text(json.dumps(index))
    ast_file.write_text(json.dumps(ast))
    assert validate(index_file,ast_file) == False


    