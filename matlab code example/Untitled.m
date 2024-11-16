vid.TriggerRepeat = Inf;
vid.FramesPerTrigger =1;
start(vid)
figure
data = getsnapshot(vid);
for jj=1:200
    data = getdata(vid);
    imshow(data,[]);
    drawnow     % update figure window
    pause(.01)
    if vid.FramesAvailable>1
        flushdata(vid);
    end
    end
stop(vid)
