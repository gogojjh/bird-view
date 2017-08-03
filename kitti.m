base_dir = '/home/csg/code/bird_veiw';
calib_dir = '/media/csg/WD/2011_09_26';

cam = 0;

% load calibration
calib = loadCalibrationCamToCam(fullfile(calib_dir,'calib_cam_to_cam.txt'));
Tr_velo_to_cam = loadCalibrationRigid(fullfile(calib_dir,'calib_velo_to_cam.txt'));

% compute projection matrix velodyne->image plane
R_cam_to_rect = eye(4);
R_cam_to_rect(1:3,1:3) = calib.R_rect{1};
P_velo_to_img = calib.P_rect{cam+1}*R_cam_to_rect*Tr_velo_to_cam;

for frame=35:294

    % load velodyne points
    fid = fopen(sprintf('%s/velodyne/data/%010d.bin',base_dir,frame),'rb');
    velo = fread(fid,[4 inf],'single')';
    velo = velo(1:5:end,:); % remove every 5th point for display speed
    fclose(fid);
    
    % remove all points behind image plane (approximation
    idx = velo(:,1)<5;
    velo(idx,:) = [];
    velo_img = project(velo(:,1:3),P_velo_to_img);
    
    f=fopen(sprintf('%s/lane/%010d.txt',base_dir,frame), 'r');
    f_w=fopen(sprintf('%s/lane_r/%010d.txt',base_dir,frame), 'w');
    
    while 1
        tline = fgetl(f);
        if ~ischar(tline),break;end
        tline = str2num(tline);
        
        fprintf(f_w, sprintf('%d\t',tline(1)));
        
        for y = 2:2:size(tline,2)
            index = -1;
            min_l = 100;
            for i=1:size(velo,1)
                % project to image plane (exclude luminance)
                tmp = abs(velo_img(i,1) - tline(y)) + abs(velo_img(i,2) - tline(y+1));
                if tmp < min_l
                    min_l = tmp;
                    index = i;
                end
            end
            fprintf(f_w, sprintf('%.3f\t%.3f\t',velo(index,1),velo(index,2)));
                    
        end
        fprintf(f_w, '\n');
        
        
    end
    fclose(f);
    fclose(f_w);
    
end
