package com.cross.beaglesight;

import android.util.Log;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesightlibs.ProtoConfig;
import com.google.android.gms.wearable.DataMap;
import com.google.protobuf.InvalidProtocolBufferException;
import com.mariux.teleport.lib.TeleportService;

/**
 * Created by cameron on 7/28/15.
 */
public class ListenService  extends TeleportService {


    @Override
    public void onCreate() {
        super.onCreate();
        Log.w("Teleport", "Teleport service started");
        //The quick way is to use setOnGetMessageTask, and set a new task
        setOnSyncDataItemTask(new StartActivityTask());
    }

    //Task that shows the path of a received message
    public class StartActivityTask extends TeleportService.OnSyncDataItemTask {

        @Override
        protected void onPostExecute(DataMap dataMap) {
            for (String key : dataMap.keySet()) {
                byte[] string = dataMap.getByteArray(key);
                if (string == null) {
                    BowManager bm = BowManager.getInstance(getApplicationContext());
                    bm.deleteBow(key);
                    Log.w("Teleport", key + " = null");
                } else {
                    try {
                        ProtoConfig.Config conf = ProtoConfig.Config.parseFrom(string);
                        BowConfig bc = new BowConfig(conf);
                        BowManager bm = BowManager.getInstance(getApplicationContext());
                        bm.saveBowConfig(bc);
                    } catch (InvalidProtocolBufferException e) {
                        Log.w("Teleport", "could not parse: " + string.toString());
                    }
                    Log.w("Teleport", key + " = " + string.toString());
                }

            }
            setOnSyncDataItemTask(new StartActivityTask());
        }
    }


}