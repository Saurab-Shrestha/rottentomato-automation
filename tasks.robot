*** Settings ***
Library    Process

*** Test Cases ***
Run Task.py Script
    Run Process    python    task.py
    
