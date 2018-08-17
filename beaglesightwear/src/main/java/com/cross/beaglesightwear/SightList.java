package com.cross.beaglesightwear;

import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.support.wear.widget.WearableLinearLayoutManager;
import android.support.wearable.activity.WearableActivity;
import android.widget.TextView;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;

import static com.cross.beaglesightwear.ShowSight.CONFIG_TAG;

public class SightList extends WearableActivity implements BowListRecyclerViewAdapter.OnListFragmentInteractionListener {

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
            BowListRecyclerViewAdapter adapter = new BowListRecyclerViewAdapter(BowManager.getInstance(getApplicationContext()).getBowList(), this);
            view.setAdapter(adapter);
        }
    }

    @Override
    public Boolean onListFragmentInteraction(BowConfig bowConfig) {
        Intent intent = new Intent(this, ShowSight.class);
        intent.putExtra(CONFIG_TAG, bowConfig.getId());
        startActivity(intent);
        return false;
    }
}
