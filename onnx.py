import matlab.engine
names = matlab.engine.find_matlab()
print(names)
# matlab.engine.shareEngine('DeepLearning')
matlab_engine = matlab.engine.connect_matlab('DeepLearning')
for x in range(6):
    matlab_engine.classify_image(nargout=0)
    image_class = matlab_engine.eval('class')
    print(image_class)

