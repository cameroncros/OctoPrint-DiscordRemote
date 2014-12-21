package com.cross.beaglesight;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.RemoteViews;


/**
 * Implementation of App Widget functionality.
 * App Widget Configuration implemented in {@link BeagleWidgetConfigureActivity BeagleWidgetConfigureActivity}
 */
public class BeagleWidget extends AppWidgetProvider {

    private static final String PlusCoarse = "PlusCoarse";
    private static final String PlusFine = "PlusFine";
    private static final String MinusCoarse = "MinusCoarse";
    private static final String MinusFine = "MinusFine";
    private static final int Fine = 1;
    private static final int Coarse = 5;


    @Override
    public void onUpdate(Context context, AppWidgetManager appWidgetManager, int[] appWidgetIds) {
        // There may be multiple widgets active, so update all of them
        final int N = appWidgetIds.length;
        for (int i = 0; i < N; i++) {
            updateAppWidget(context, appWidgetManager, appWidgetIds[i]);

        }
    }

    @Override
    public void onDeleted(Context context, int[] appWidgetIds) {
        // When the user deletes the widget, delete the preference associated with it.
        final int N = appWidgetIds.length;
        for (int i = 0; i < N; i++) {
            BeagleWidgetConfigureActivity.deleteTitlePref(context, appWidgetIds[i]);
            BeagleWidgetConfigureActivity.deleteDistPref(context, appWidgetIds[i]);
        }
    }

    @Override
    public void onEnabled(Context context) {
        // Enter relevant functionality for when the first widget is created
    }

    @Override
    public void onDisabled(Context context) {
        // Enter relevant functionality for when the last widget is disabled
    }

    @Override
    public void onReceive(Context context, Intent intent) {
        String action = intent.getAction();

        Bundle bundle = intent.getExtras();
        for (String key : bundle.keySet()) {
            Object value = bundle.get(key);
            Log.d("BeagleSight", String.format("%s %s (%s)", key,
                    value.toString(), value.getClass().getName()));
        }
        int appWidgetId = intent.getIntExtra("widgetId", -1);
        if (appWidgetId == -1) {
            return;
        }
        int dist=20;
        //super.onReceive(context, intent);
        switch (intent.getAction()) {
            case PlusCoarse:
                dist = BeagleWidgetConfigureActivity.loadDistancePref(context, appWidgetId);
                dist += Coarse;
                BeagleWidgetConfigureActivity.saveDistancePref(context, appWidgetId, dist);
                break;
            case PlusFine:
                dist = BeagleWidgetConfigureActivity.loadDistancePref(context, appWidgetId);
                dist += Fine;
                BeagleWidgetConfigureActivity.saveDistancePref(context, appWidgetId, dist);
                break;
            case MinusCoarse:
                dist = BeagleWidgetConfigureActivity.loadDistancePref(context, appWidgetId);
                dist -= Coarse;
                BeagleWidgetConfigureActivity.saveDistancePref(context, appWidgetId, dist);
                break;
            case MinusFine:
                dist = BeagleWidgetConfigureActivity.loadDistancePref(context, appWidgetId);
                dist -= Fine;
                BeagleWidgetConfigureActivity.saveDistancePref(context, appWidgetId, dist);
                break;
        }

        AppWidgetManager appWidgetManager = AppWidgetManager.getInstance(context);

        updateAppWidget(context, appWidgetManager, appWidgetId);
    }


    static void updateAppWidget(Context context, AppWidgetManager appWidgetManager,
                                int appWidgetId) {
        // Construct the RemoteViews object
        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.beagle_widget);

        views.setOnClickPendingIntent(R.id.imageButtonPlusCoarse,  getPendingSelfIntent(context, PlusCoarse,  appWidgetId));
        views.setOnClickPendingIntent(R.id.imageButtonPlusFine,    getPendingSelfIntent(context, PlusFine,    appWidgetId));
        views.setOnClickPendingIntent(R.id.imageButtonMinusCoarse, getPendingSelfIntent(context, MinusCoarse, appWidgetId));
        views.setOnClickPendingIntent(R.id.imageButtonMinusFine,   getPendingSelfIntent(context, MinusFine,   appWidgetId));

        String bowname = BeagleWidgetConfigureActivity.loadTitlePref(context, appWidgetId);
        int dist = BeagleWidgetConfigureActivity.loadDistancePref(context, appWidgetId);

        BowManager bm = BowManager.getInstance(null);
        PositionCalculator pc = bm.getPositionCalculator(bowname);

        if (pc == null) {
            return;
        }

        double pos = pc.calcPosition(dist);

        views.setTextViewText(R.id.widgetDistance, PositionCalculator.getDisplayValue(dist,0));
        views.setTextViewText(R.id.widgetPosition, PositionCalculator.getDisplayValue(pos, 2));
        views.setTextViewText(R.id.widgetBowName, bowname);

        // Instruct the widget manager to update the widget
        appWidgetManager.updateAppWidget(appWidgetId, views);
    }

    protected static PendingIntent getPendingSelfIntent(Context context, String action, int appWidgetId) {
        Log.w("BeagleSight", "Appwidgetid:"+appWidgetId);
        Intent intent = new Intent(context, BeagleWidget.class);
        intent.setAction(action);
        intent.putExtra("widgetId", appWidgetId);
        return PendingIntent.getBroadcast(context, 0, intent, 0);
    }
}


