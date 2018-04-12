package com.cross.beaglesightlibs;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.pm.PackageManager;
import android.os.Environment;
import android.util.Log;
import android.widget.Toast;

import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;

import org.xml.sax.SAXException;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.Vector;

import javax.xml.parsers.ParserConfigurationException;


public class BowManager {
    @SuppressLint("StaticFieldLeak")
    private static volatile BowManager instance = null;
    private Context cont = null;
    private List<BowConfig> bowList;
    private File folder = null;

    private BowManager(Context cont) {
        bowList = new Vector<>();
        setContext(cont);
    }

    private void loadBows() {
        bowList.clear();
        if (folder != null && folder.exists()) {
            File[] listOfFiles = folder.listFiles();
            for (File fl : listOfFiles) {
                try {
                    BowConfig bowConfig = new BowConfig(fl);
                    bowList.add(bowConfig);
                } catch (IOException | ParserConfigurationException | SAXException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    public void saveBows() {
        if (folder != null && folder.exists()) {
            File[] listOfFiles = folder.listFiles();
            for (File fl : listOfFiles) {
                fl.delete();
            }
            for (BowConfig bowConfig : bowList) {
                String filename = folder + File.separator + bowConfig.getId();
                try {
                    FileOutputStream fileOS = new FileOutputStream(filename, false);
                    bowConfig.save(fileOS);
                } catch (FileNotFoundException e) {
                    Toast.makeText(cont, e.toString(), Toast.LENGTH_LONG).show();
                }
            }
        }
    }

	public void addBowConfig(BowConfig bowConfig)
	{
	    if (bowConfig != null) {
            deleteBowConfig(bowConfig);
            bowList.add(bowConfig);
            saveBows();
        }
	}

	public static BowManager getInstance(Context cont) {
        synchronized (BowManager.class) {
            if (instance == null && cont != null) {
                instance = new BowManager(cont);
                instance.loadBows();
            }
        }
		return instance;
	}

	public List<BowConfig> getBowList() {
		return bowList;
	}

	public BowConfig getBowConfig(String id) throws InvalidBowConfigIdException {
        for (BowConfig bowConfig : bowList)
		{
			if (bowConfig.getId().equals(id)) {
				return bowConfig;
			}
		}
		throw new InvalidBowConfigIdException();
	}

	private void setContext(Context cont) {
		this.cont = cont;
        folder = new File(cont.getFilesDir()+File.separator+"bows"+File.separator);
        if (!folder.exists() && !folder.mkdirs()) {
            Log.e("BeagleSight", "Cant create the bow folder or the folder wasnt found");
            folder=null;
        }
		// TODO: Configure wear transfer
	}

	public void deleteBowConfig(BowConfig bowConfig) {
		try {
			File file = new File(folder + File.separator + bowConfig.getId());
			file.delete();
			Log.w("BowManager", "deleted " + file.getAbsolutePath());

			if (!cont.getPackageManager().hasSystemFeature(PackageManager.FEATURE_WATCH)) {
				//TODO: Delete from wear as well
			}
			bowList.remove(bowConfig);
		} catch (NullPointerException e) {
			//do nothing
		}
	}
}