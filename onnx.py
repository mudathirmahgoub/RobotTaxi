import matlab.engine
names = matlab.engine.find_matlab()
print(names)
matlab_engine = matlab.engine.connect_matlab('DeepLearning')
for x in range(6):
    matlab_engine.classifyImage(nargout=0)
    image_class = matlab_engine.eval('class')
    print(image_class)

