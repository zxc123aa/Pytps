import os

def getList(app):
    fileList=os.listdir(app.imagePath)
    imageList=[]
    for i in range(len(fileList)):
        if fileList[i].endswith(".tif") or fileList[i].endswith(".tiff") or fileList[i].endswith(".jpg") or fileList[i].endswith(".png") or fileList[i].endswith(".raw"):
            imageList.append(fileList[i])
        else:
            pass

    app.ui.listWidget.addItems(imageList)