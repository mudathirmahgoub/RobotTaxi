% return the class of the image and its probability
datastore = imageDatastore('data','IncludeSubfolders',true,'LabelSource','foldernames');
augmentedImages = augmentedImageDatastore([224 224],datastore);
[classes,probabilities] = classify(netTransfer,augmentedImages);
class = string(classes(1));
probability = probabilities(1, :);


