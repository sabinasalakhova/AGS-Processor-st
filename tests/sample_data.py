"""Sample AGS4 data for testing."""

SAMPLE_AGS4_CONTENT = '''
"GROUP","PROJ"
"HEADING","PROJ_ID","PROJ_NAME","PROJ_LOC","PROJ_CLNT","PROJ_CONT","PROJ_ENG"
"UNIT","","","","","",""
"TYPE","X","X","X","X","X","X"
"DATA","123456","Sample Project","Sample Location","Sample Client","Sample Contractor","Sample Engineer"

"GROUP","TRAN"
"HEADING","TRAN_ISNO","TRAN_DATE","TRAN_PROD","TRAN_STAT","TRAN_DESC","TRAN_AGS","TRAN_RECV","TRAN_DLIM","TRAN_RCON","TRAN_REM"
"UNIT","","yyyy-mm-dd","","","","","","","",""
"TYPE","X","DT","X","X","X","X","X","X","X","X"
"DATA","1","2024-01-01","AGS Processor","Final","Sample AGS4 file","4.0.4","","","",""

"GROUP","LOCA"
"HEADING","LOCA_ID","LOCA_TYPE","LOCA_NATE","LOCA_NATN","LOCA_GREF","LOCA_GL","LOCA_FDEP"
"UNIT","","","m","m","","m","m"
"TYPE","ID","PA","2DP","2DP","X","2DP","2DP"
"DATA","BH01","BOREHOLE","523456.12","178945.67","WGS84","100.50","15.00"
"DATA","BH02","BOREHOLE","523478.34","178923.45","WGS84","99.75","12.50"

"GROUP","GEOL"
"HEADING","LOCA_ID","GEOL_TOP","GEOL_BASE","GEOL_DESC","GEOL_GEOL","GEOL_LEG"
"UNIT","","m","m","","",""
"TYPE","ID","2DP","2DP","X","X","X"
"DATA","BH01","0.00","2.50","Made Ground","MADE GROUND","MG"
"DATA","BH01","2.50","5.00","Clay - brown, stiff","CLAY","CL"
"DATA","BH01","5.00","15.00","Sand - medium dense","SAND","SD"
"DATA","BH02","0.00","1.50","Topsoil","TOPSOIL","TS"
"DATA","BH02","1.50","8.00","Clay - grey, firm to stiff","CLAY","CL"
"DATA","BH02","8.00","12.50","Gravel - sandy","GRAVEL","GR"

"GROUP","SAMP"
"HEADING","LOCA_ID","SAMP_ID","SAMP_TOP","SAMP_BASE","SAMP_TYPE","SAMP_REF","SAMP_DESC"
"UNIT","","","m","m","","",""
"TYPE","ID","ID","2DP","2DP","X","X","X"
"DATA","BH01","S1","1.00","1.45","U","BH01-S1","Disturbed sample"
"DATA","BH01","S2","3.00","3.45","U","BH01-S2","Bulk sample"
"DATA","BH02","S1","2.00","2.45","U","BH02-S1","Disturbed sample"
'''

def create_sample_ags4_file(filepath: str):
    """Create a sample AGS4 file for testing."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(SAMPLE_AGS4_CONTENT.strip())
