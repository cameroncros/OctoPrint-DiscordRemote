package com.cross.beaglesight.widget;

import android.app.Activity;
import android.appwidget.AppWidgetManager;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Spinner;

import com.cross.beaglesight.R;
import com.cross.beaglesightlibs.BowManager;

import java.util.ArrayList;
import java.util.Map;


/**
 * The configuration screen for the {@link BeagleWidget BeagleWidget} AppWidget.
 */
public class BeagleWidgetConfigureActivity extends Activity {

    int mAppWidgetId = AppWidgetManager.INVALID_APPWIDGET_ID;
    private static final String PREFS_NAME = "com.cross.beaglesight.widget.BeagleWidget";
    private static final String PREF_PREFIX_NAME = "appwidgetname_";
    private static final String PREF_PREFIX_DIST = "appwidgetdist_";

    public BeagleWidgetConfigureActivity() {
        super();
    }

    @Override
    public void onCreate(Bundle icicle) {
        super.onCreate(icicle);

        // Set the result to CANCELED.  This will cause the widget host to cancel
        // out of the widget placement if the user presses the back button.
        setResult(RESULT_CANCELED);

        setContentView(R.layout.beagle_widget_configure);
        findViewById(R.id.add_button).setOnClickListener(mOnClickListener);

        // Find the widget id from the intent.
        Intent intent = getIntent();
        Bundle extras = intent.getExtras();
        if (extras != null) {
            mAppWidgetId = extras.getInt(
                    AppWidgetManager.EXTRA_APPWIDGET_ID, AppWidgetManager.INVALID_APPWIDGET_ID);
        }

        // If this activity was started with an intent without an app widget ID, finish with an error.
        if (mAppWidgetId == AppWidgetManager.INVALID_APPWIDGET_ID) {
            finish();
            return;
        }

        Spinner spinner = (Spinner) findViewById(R.id.bowListSpinner);
        // Create an ArrayAdapter using the string array and a default spinner layout
        BowManager bm = BowManager.getInstance(this);
        ArrayList<String> bows = new ArrayList<String>(bm.getBowList());
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, android.R.layout.simple_spinner_dropdown_item, bows);
        // Apply the adapter to the spinner
        spinner.setAdapter(adapter);
    }

    View.OnClickListener mOnClickListener = new View.OnClickListener() {
        public void onClick(View v) {
            final Context context = BeagleWidgetConfigureActivity.this;

            // When the button is clicked, store the string locally
            Spinner mySpinner=(Spinner) findViewById(R.id.bowListSpinner);
            String choice = mySpinner.getSelectedItem().toString();
            saveTitlePref(context, mAppWidgetId, choice);
            saveDistancePref(context, mAppWidgetId, 20);
            // It is the responsibility of the configuration activity to update the app widget
            AppWidgetManager appWidgetManager = AppWidgetManager.getInstance(context);
            BeagleWidget.updateAppWidget(context, appWidgetManager, mAppWidgetId);

            // Make sure we pass back the original appWidgetId
            Intent resultValue = new Intent();
            resultValue.putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, mAppWidgetId);
            setResult(RESULT_OK, resultValue);
            finish();
        }
    };

    // Write the prefix to the SharedPreferences object for this widget
    static void saveTitlePref(Context context, int appWidgetId, String text) {
        SharedPreferences.Editor prefs = context.getSharedPreferences(PREFS_NAME, 0).edit();
        prefs.putString(PREF_PREFIX_NAME + appWidgetId, text);
        prefs.commit();
    }

    // Read the prefix from the SharedPreferences object for this widget.
    // If there is no preference saved, get the default from a resource
    static String loadTitlePref(Context context, int appWidgetId) {
        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        Map<String,?> keys = prefs.getAll();

        for(Map.Entry<String,?> entry : keys.entrySet()){
            Log.d("BeagleSight map values", entry.getKey() + ": " +
                    entry.getValue().toString());
        }
        String titleValue = prefs.getString(PREF_PREFIX_NAME + appWidgetId, context.getString(R.string.app_name));
        return titleValue;

    }

    static void deleteTitlePref(Context context, int appWidgetId) {
        SharedPreferences.Editor prefs = context.getSharedPreferences(PREFS_NAME, 0).edit();
        prefs.remove(PREF_PREFIX_NAME + appWidgetId);
        prefs.commit();
    }

    // Write the prefix to the SharedPreferences object for this widget
    static void saveDistancePref(Context context, int appWidgetId, int dist) {
        SharedPreferences.Editor prefs = context.getSharedPreferences(PREFS_NAME, 0).edit();
        prefs.putInt(PREF_PREFIX_DIST + appWidgetId, dist);
        prefs.commit();
    }

    // Read the prefix from the SharedPreferences object for this widget.
    // If there is no preference saved, get the default from a resource
    static int loadDistancePref(Context context, int appWidgetId) {

        SharedPreferences prefs = context.getSharedPreferences(PREFS_NAME, 0);
        int titleValue = prefs.getInt(PREF_PREFIX_DIST + appWidgetId, 20);
        return titleValue;

    }

    static void deleteDistPref(Context context, int appWidgetId) {
        SharedPreferences.Editor prefs = context.getSharedPreferences(PREFS_NAME, 0).edit();
        prefs.remove(PREF_PREFIX_DIST + appWidgetId);
        prefs.commit();
    }
}



