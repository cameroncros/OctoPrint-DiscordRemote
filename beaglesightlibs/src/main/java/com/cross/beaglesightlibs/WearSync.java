package com.cross.beaglesightlibs;

import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Build;

import com.google.android.gms.wearable.DataClient;
import com.google.android.gms.wearable.DataMap;
import com.google.android.gms.wearable.PutDataMapRequest;
import com.google.android.gms.wearable.PutDataRequest;
import com.google.android.gms.wearable.Wearable;

import java.io.ByteArrayOutputStream;

public class WearSync {
    public static final String BOWCONFIGS = "/bowconfigs";
    private final DataClient dataClient;
    private PutDataMapRequest dataMapRequest = PutDataMapRequest.create(BOWCONFIGS);
    private boolean isPhone;

    public WearSync(Context cont)
    {
        this.isPhone = Build.VERSION.SDK_INT < Build.VERSION_CODES.KITKAT_WATCH ||
                !cont.getPackageManager().hasSystemFeature(PackageManager.FEATURE_WATCH);
        dataMapRequest.setUrgent();
        dataClient = Wearable.getDataClient(cont);
    }

    public void addBowConfig(BowConfig bowConfig) {
        if (isPhone) {
            DataMap dataMap = dataMapRequest.getDataMap();
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            bowConfig.save(baos);
            dataMap.putByteArray(bowConfig.getId(), baos.toByteArray());
            PutDataRequest dataRequest = dataMapRequest.asPutDataRequest();
            dataClient.putDataItem(dataRequest);
        }
    }

    public void removeBowConfig(BowConfig bowConfig) {
        if (isPhone) {
            DataMap dataMap = dataMapRequest.getDataMap();
            dataMap.remove(bowConfig.getId());
            PutDataRequest dataRequest = dataMapRequest.asPutDataRequest();
            dataClient.putDataItem(dataRequest);
        }
    }
}
