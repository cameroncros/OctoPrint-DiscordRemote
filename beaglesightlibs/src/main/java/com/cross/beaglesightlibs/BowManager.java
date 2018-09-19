package com.cross.beaglesightlibs;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;
import android.widget.Toast;

import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;


public class BowManager {
    @SuppressLint("StaticFieldLeak")
    private static volatile BowManager instance = null;
    private SharedPreferences savedConfigs = null;
    private Context cont;
    private WearSync wearSync;

    private BowManager(Context cont) {
        assert cont != null;
        this.wearSync = new WearSync(cont);
        this.cont = cont;
        this.savedConfigs = cont.getSharedPreferences("savedConfigs", Context.MODE_PRIVATE);
    }

    public static BowManager getInstance(Context cont) {
        synchronized (BowManager.class) {
            if (instance == null && cont != null) {
                instance = new BowManager(cont);
                if (instance.getBowList().size() == 0 && Build.FINGERPRINT.contains("generic"))
                {
                    loadFakeBows();
                }
            }
        }
        return instance;
    }

    private static void loadFakeBows() {
        {
            BowConfig bc = new BowConfig("Fake bow1", "This is a testing bow, if you see this in a live app, i fucked up.");
            bc.addPosition(new PositionPair(10, 10));
            bc.addPosition(new PositionPair(20, 15));
            bc.addPosition(new PositionPair(30, 40));
            instance.addBowConfig(bc);
        }
        {
            BowConfig bc = new BowConfig("Fake bow2", "This is a testing bow, if you see this in a live app, i fucked up.");
            bc.addPosition(new PositionPair(10, 40));
            bc.addPosition(new PositionPair(20, 15));
            bc.addPosition(new PositionPair(30, 10));
            instance.addBowConfig(bc);
        }
        for (int i = 0; i < 10; i++)
        {
            BowConfig bc = new BowConfig("Fake bow" + (i+2), "This is a testing bow, if you see this in a live app, i fucked up.");
            bc.addPosition(new PositionPair((float)Math.random()*40-10, (float)Math.random()*40-10));
            bc.addPosition(new PositionPair((float)Math.random()*40-10, (float)Math.random()*40-10));
            bc.addPosition(new PositionPair((float)Math.random()*40-10, (float)Math.random()*40-10));
            instance.addBowConfig(bc);
        }
    }

    public void addBowConfig(BowConfig bowConfig)
    {
        if (bowConfig == null) {
            return;
        }
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        bowConfig.save(baos);
        String configString =
                new String(baos.toByteArray(), Charset.forName("UTF-8"));
        savedConfigs.edit().putString(bowConfig.getId(), configString).apply();

        wearSync.addBowConfig(bowConfig);
    }

    public BowConfig getBowConfig(String id) throws InvalidBowConfigIdException {
        String configString = this.savedConfigs.getString(id, "");

        try {
            InputStream stream = new ByteArrayInputStream(configString.getBytes(Charset.forName("UTF-8")));
            BowConfig config = new BowConfig(stream);
            wearSync.addBowConfig(config);
            return config;
        }
        catch (Exception e)
        {
            throw new InvalidBowConfigIdException(e);
        }
    }

    public void deleteBowConfig(String id) {
        this.savedConfigs.edit().remove(id).apply();
        wearSync.removeBowConfig(id);
    }

	public List<BowConfig> getBowList() {
        List<BowConfig> bowList = new ArrayList<>();
        for (String key : savedConfigs.getAll().keySet())
        {
            try {
                bowList.add(getBowConfig(key));
            }
            catch(InvalidBowConfigIdException e)
            {
                Toast.makeText(cont, e.getMessage(), Toast.LENGTH_LONG).show();
            }
        }
		return bowList;
	}
}
