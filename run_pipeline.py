from backend.orchestrator.pipeline_runner import run_reconciliation_pipeline

run_reconciliation_pipeline(
    input_excel_path=r"C:\Users\hasan\DataScience\Work\RTO_Reco\Raw\Dec\BR-RTO-DEC-21.xlsx",
    output_excel_path=r"C:\Users\hasan\DataScience\Work\RTO_Reco\Processed\Dec\Test_BR_4.xlsx"
)