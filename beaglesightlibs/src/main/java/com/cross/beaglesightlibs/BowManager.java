package com.cross.beaglesightlibs;

import android.annotation.SuppressLint;
import android.content.Context;
import android.os.AsyncTask;
import android.os.Build;
import android.support.annotation.NonNull;
import android.util.Log;

import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;

import org.xml.sax.SAXException;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.ParserConfigurationException;


public class BowManager {
    @SuppressLint("StaticFieldLeak")
    private static volatile BowManager instance = null;
    private List<BowConfig> bowList = new ArrayList<>();
    private WearSync wearSync;
    private File folder;


    private BowManager(Context cont) {
        assert cont != null;
        this.wearSync = new WearSync(cont);
        folder = new File(cont.getFilesDir()+File.separator+"bows");
        if (!folder.exists() && !folder.mkdir()) {
            Log.e("BeagleSight", "Cant create the bow folder or the folder wasnt found");
            folder=null;
        }
    }

    public static BowManager getInstance(Context cont) {
        synchronized (BowManager.class) {
            if (instance == null && cont != null) {
                instance = new BowManager(cont);
            }
        }
        return instance;
    }

    public interface LoadCallback {
        void onResult(List<BowConfig> results);
    }

    public void loadBows(LoadCallback callback)
    {
        // This enforces that the BowManager instance has already been created.
        BowManager.loadBowsStatic(callback);
        if (bowList.size() == 0 && Build.FINGERPRINT.contains("generic"))
        {
            loadFakeBows();
        }
    }

    private static void loadBowsStatic(final LoadCallback callback)
    {
        new AsyncTask<Void, Void, List<BowConfig>>() {
            @Override
            protected List<BowConfig> doInBackground(Void... params) {
                instance.bowList.clear();
                if (instance.folder != null) {
                    File[] listOfFiles = instance.folder.listFiles();
                    for (File fl : listOfFiles) {
                        try {
                            FileInputStream fis = new FileInputStream(fl);
                            BowConfig bc = new BowConfig(fis);
                            instance.bowList.add(bc);
                            instance.wearSync.addBowConfig(bc);
                        }
                        catch (ParserConfigurationException | IOException | SAXException e) {
                            Log.e("BeagleSight", "Failed to load bow: " + e.getMessage());
                        }
                    }
                }
                return instance.bowList;
            }

            @Override
            protected void onPostExecute(List<BowConfig> result)
            {
                callback.onResult(result);
            }
        }.execute();
    }

    private static void saveBowStatic(final BowConfig bowConfig)
    {
        new AsyncTask<Void, Void, Boolean>() {
            @Override
            protected Boolean doInBackground(Void... params) {
                File bowConfigFile = getBowConfigFile(bowConfig);
                FileOutputStream fos = null;
                try {
                    fos = new FileOutputStream(bowConfigFile);
                } catch (FileNotFoundException e) {
                    Log.e("BeagleSight", "Failed to save to disk, could not find file location");
                    return false;
                }
                bowConfig.save(fos);
                return true;
            }
        }.execute();
    }

    private void loadFakeBows() {
        {
            BowConfig bc = new BowConfig("Fake bow1", "This is a testing bow, if you see this in a live app, i fucked up.");
            bc.addPosition(new PositionPair(10, 10));
            bc.addPosition(new PositionPair(20, 15));
            bc.addPosition(new PositionPair(30, 40));
            addBowConfig(bc);
        }
        {
            BowConfig bc = new BowConfig("Fake bow2", "This is a testing bow, if you see this in a live app, i fucked up.");
            bc.addPosition(new PositionPair(10, 40));
            bc.addPosition(new PositionPair(20, 15));
            bc.addPosition(new PositionPair(30, 10));
            addBowConfig(bc);
        }
        for (int i = 0; i < 10; i++)
        {
            BowConfig bc = new BowConfig("Fake bow" + (i+2), "This is a testing bow, if you see this in a live app, i fucked up.");
            bc.addPosition(new PositionPair((float)Math.random()*40-10, (float)Math.random()*40-10));
            bc.addPosition(new PositionPair((float)Math.random()*40-10, (float)Math.random()*40-10));
            bc.addPosition(new PositionPair((float)Math.random()*40-10, (float)Math.random()*40-10));
            addBowConfig(bc);
        }
    }

    @NonNull
    private static File getBowConfigFile(BowConfig bowConfig) {
        return new File(instance.folder.getPath() + File.separator + bowConfig.getId());
    }

    public void addBowConfig(BowConfig bowConfig)
    {
        if (bowConfig == null) {
            return;
        }

        saveBowStatic(bowConfig);

        bowList.add(bowConfig);
        wearSync.addBowConfig(bowConfig);
    }

    public BowConfig getBowConfig(String id) throws InvalidBowConfigIdException {
        for (BowConfig bowConfig : bowList)
        {
            if (bowConfig.getId().compareTo(id) == 0)
            {
                return bowConfig;
            }
        }
        throw new InvalidBowConfigIdException();
    }

    public void deleteBowConfig(BowConfig bowConfig) {
        File bowConfigFile = getBowConfigFile(bowConfig);
        bowConfigFile.delete();

        bowList.remove(bowConfig);
        wearSync.removeBowConfig(bowConfig);
    }

	public List<BowConfig> getBowList() {
		return bowList;
	}
}
