package com.cross.beaglesightlibs;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.widget.Toast;

import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;


public class BowManager {
    @SuppressLint("StaticFieldLeak")
    private static volatile BowManager instance = null;
    private SharedPreferences savedConfigs = null;
    private Context cont;

    private BowManager(Context cont) {
        setContext(cont);
    }

    private void setContext(Context cont) {
        this.cont = cont;
        this.savedConfigs = cont.getSharedPreferences("savedConfigs", Context.MODE_PRIVATE);
    }

    public static BowManager getInstance(Context cont) {
        synchronized (BowManager.class) {
            if (instance == null && cont != null) {
                instance = new BowManager(cont);
            }
        }
        return instance;
    }

	public void addBowConfig(BowConfig bowConfig)
	{
	    if (bowConfig != null) {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            bowConfig.save(baos);
            String configString =
                    new String(baos.toByteArray(), Charset.forName("UTF-8"));
            savedConfigs.edit().putString(bowConfig.getId(), configString).apply();
        }
	}

    public BowConfig getBowConfig(String id) throws InvalidBowConfigIdException {
        String configString = this.savedConfigs.getString(id, "");
        try {
            InputStream stream = new ByteArrayInputStream(configString.getBytes(Charset.forName("UTF-8")));
            return new BowConfig(stream);
        }
        catch (Exception e)
        {
            throw new InvalidBowConfigIdException(e);
        }
    }

    public void deleteBowConfig(BowConfig bowConfig) {
        this.savedConfigs.edit().remove(bowConfig.getId()).apply();
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