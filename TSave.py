import numpy as np

def save_ini(app):
    initFile=[[0 for _ in range(2)] for _ in range(24)]  # 扩展到24行（新增fadeRadius）
    initFile[0][0]="imagepath="
    initFile[0][1]=str(app.imagePath)
    initFile[1][0]="savepath="
    initFile[1][1]=str(app.savePath)
    initFile[2][0]="MCPpath="
    initFile[2][1]=str(app.MCPPath)
    initFile[3][0]="X0="
    initFile[3][1]=str(app.X0)
    initFile[4][0]="Y0="
    initFile[4][1]=str(app.Y0)
    initFile[5][0]="±dY="
    initFile[5][1]=str(app.dY)
    initFile[6][0]="colormin="
    initFile[6][1]=str(app.colormin)
    initFile[7][0]="colormax="
    initFile[7][1]=str(app.colormax)
    initFile[8][0]="Emin="
    initFile[8][1]=str(app.Emin)
    initFile[9][0]="Emax="
    initFile[9][1]=str(app.Emax)
    initFile[10][0]="specEmin="
    initFile[10][1]=str(app.specEmin)
    initFile[11][0]="specEmax="
    initFile[11][1]=str(app.specEmax)
    initFile[12][0]="specdNdEmin="
    initFile[12][1]=str(app.specdNdEmin)
    initFile[13][0]="specdNdEmax="
    initFile[13][1]=str(app.specdNdEmax)
    initFile[14][0]="specWindow="
    initFile[14][1]=str(app.specWindow)
    # 滤波配置（新增）
    initFile[15][0]="filterMode="
    initFile[15][1]=str(app.filterMode)
    initFile[16][0]="medianSize="
    initFile[16][1]=str(app.medianSize)
    initFile[17][0]="medianIterations="
    initFile[17][1]=str(app.medianIterations)
    initFile[18][0]="morphologicalSize="
    initFile[18][1]=str(app.morphologicalSize)
    initFile[19][0]="rollingBallRadius="
    initFile[19][1]=str(app.rollingBallRadius)
    # 轨迹保护滤波参数（新增）
    initFile[20][0]="protectionWidth="
    initFile[20][1]=str(app.protectionWidth)
    initFile[21][0]="aggressiveSize="
    initFile[21][1]=str(app.aggressiveSize)
    initFile[22][0]="gentleSize="
    initFile[22][1]=str(app.gentleSize)
    # 软掩膜羽化半径（新增）
    initFile[23][0]="fadeRadius="
    initFile[23][1]=str(app.fadeRadius if hasattr(app, 'fadeRadius') else 20)
    np_initFile=np.array(initFile,dtype=str)

    np.savetxt("./PyTPS_init.ini",np_initFile,fmt='%s',delimiter='\t',newline='\n',encoding='utf-8')