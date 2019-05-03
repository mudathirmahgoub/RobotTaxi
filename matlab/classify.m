% return the class of an image
function [class] = classify_image(directory, robotType)
    if strcmp(robotType, 'cozmo')
        netTransfer = evalin('base', 'netTransferCozmo');    
    end
    datastore = imageDatastore(directory,'IncludeSubfolders',true,'LabelSource','foldernames');
    augmentedImages = augmentedImageDatastore([224 224],datastore);
    [classes,probabilities] = classify(netTransfer,augmentedImages);
    class = string(classes(1));
    probability = probabilities(1, :);    
end
