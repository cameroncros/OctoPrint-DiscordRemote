package com.cross.beaglesightwear;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.google.android.gms.wearable.Asset;
import com.google.android.gms.wearable.DataEvent;
import com.google.android.gms.wearable.DataEventBuffer;
import com.google.android.gms.wearable.DataMapItem;
import com.google.android.gms.wearable.WearableListenerService;

import org.xml.sax.SAXException;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.Charset;

import javax.xml.parsers.ParserConfigurationException;

import static com.cross.beaglesightlibs.BowManager.configkey;

public class ListenerService extends WearableListenerService {
    public ListenerService() {
    }

    @Override
    public void onDataChanged(DataEventBuffer dataEvents) {
        for (DataEvent event : dataEvents) {
            if (event.getType() == DataEvent.TYPE_CHANGED) {
                DataMapItem dataMapItem = DataMapItem.fromDataItem(event.getDataItem());
                Asset profileAsset = dataMapItem.getDataMap().getAsset(configkey);
                byte[] configBytes = profileAsset.getData();
                ByteArrayInputStream bais = new ByteArrayInputStream(configBytes);
                try {
                    BowConfig bc = new BowConfig(bais);
                    BowManager.getInstance(this.getApplicationContext()).addBowConfig(bc, false);
                } catch (IOException | ParserConfigurationException | SAXException e) {
                    e.printStackTrace();
                }

                String configString = new String(configBytes, Charset.forName("UTF-8"));
                //savedConfigs.edit().putString(event.getDataItem().getUri().getPath(), configString).apply();

            }
            if (event.getType() == DataEvent.TYPE_DELETED) {
                //TODO: Handle delete
            }
        }
    }
}
