package com.cross.beaglesight;

import android.app.Application;
import android.content.res.Configuration;

import org.acra.*;
import org.acra.annotation.*;
import org.acra.sender.HttpSender;

/**
 * Created by cameron on 8/4/15.
 */

@ReportsCrashes(httpMethod = HttpSender.Method.PUT,
        reportType = HttpSender.Type.JSON,
        formUri = "http://192.168.1.100:5984/acra-beaglesight/_design/acra-storage/_update/report",
        formUriBasicAuthLogin = "BeagleReporter",
        formUriBasicAuthPassword = "beagle")
public class MyApplication extends Application {
    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
    }

    @Override
    public void onCreate() {
        super.onCreate();
        ACRA.init(this);
    }

    @Override
    public void onLowMemory() {
        super.onLowMemory();
    }

    @Override
    public void onTerminate() {
        super.onTerminate();
    }
}
