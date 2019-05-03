% net = googlenet;
run('C:\temp\robotics\RobotTaxi\matlab\create_network.mlx')
imds = imageDatastore('training_images/cozmo','IncludeSubfolders',true,'LabelSource','foldernames');
[imdsTrain,imdsValidation] = splitEachLabel(imds,0.7,'randomized');

augimdsTrain = augmentedImageDatastore([224 224],imdsTrain);
augimdsValidation = augmentedImageDatastore([224 224],imdsValidation);

options = trainingOptions('sgdm', ...
    'MiniBatchSize',10, ...
    'MaxEpochs',6, ...
    'Shuffle','every-epoch', ...
    'InitialLearnRate',1e-4, ...
    'ValidationData',augimdsValidation, ...
    'ValidationFrequency',6, ...
    'Verbose',false, ...
    'Plots','training-progress');

netTransferCozmo = trainNetwork(augimdsTrain,lgraph,options);

[YPred,probs] = classify(netTransferCozmo,augimdsValidation);
accuracy = mean(YPred == imdsValidation.Labels)

idx = randperm(numel(augimdsValidation.Files),4);
figure
for i = 1:4
    subplot(2,2,i)
    I = readimage(imdsValidation,idx(i));
    imshow(I)
    label = YPred(idx(i));
    title(string(label) + ", " + num2str(100*max(probs(idx(i),:)),3) + "%");
end