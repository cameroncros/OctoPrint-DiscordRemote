package com.cross.beaglesight;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.support.v7.widget.RecyclerView;
import android.support.wear.widget.WearableLinearLayoutManager;
import android.support.wearable.activity.WearableActivity;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;

import java.util.List;

import static com.cross.beaglesight.ListenerService.REFRESH_DATA;
import static com.cross.beaglesight.ShowSight.CONFIG_TAG;

public class SightList extends WearableActivity implements BowListRecyclerViewAdapter.OnListFragmentInteractionListener {

    private BowListRecyclerViewAdapter adapter;
    private BroadcastReceiver receiver;
    private List<BowConfig> configList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sight_list);

        // Enables Always-on
        setAmbientEnabled();

        RecyclerView view = findViewById(R.id.bowlistrecyclerview);
        // Set the adapter
        if (view != null) {
            Context context = view.getContext();
            view.setLayoutManager(new WearableLinearLayoutManager(context));
            configList = BowManager.getInstance(getApplicationContext()).getBowList();
            adapter = new BowListRecyclerViewAdapter(configList, this);
            view.setAdapter(adapter);
        }

        // Setup broadcast receiver
        IntentFilter filter = new IntentFilter(REFRESH_DATA);
        receiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                configList.clear();
                configList.addAll(BowManager.getInstance(getApplicationContext()).getBowList());
                adapter.notifyDataSetChanged();
            }
        };
        registerReceiver(receiver, filter);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        unregisterReceiver(receiver);
    }

    @Override
    public Boolean onListFragmentInteraction(BowConfig bowConfig) {
        Intent intent = new Intent(this, ShowSight.class);
        intent.putExtra(CONFIG_TAG, bowConfig.getId());
        startActivity(intent);
        return false;
    }
}
