package com.cross.beaglesightwear;

import android.content.Intent;
import android.os.Bundle;
import android.support.wearable.activity.WearableActivity;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;
import com.cross.beaglesightwear.views.SightGraphWear;

public class ShowSight extends WearableActivity {
    static final String CONFIG_TAG = "config";

    private BowConfig bowConfig;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_show_sight);

        Intent intent = getIntent();
        String id = (String) intent.getSerializableExtra(CONFIG_TAG);
        try {
             bowConfig = BowManager.getInstance(this).getBowConfig(id);
        } catch (InvalidBowConfigIdException e) {
            Toast.makeText(this,"Invalid bow config", Toast.LENGTH_LONG).show();
            finish();
        }

        SightGraphWear sightGraphWear = findViewById(R.id.sightGraph);
        sightGraphWear.setBowConfig(bowConfig);

        ImageView button = findViewById(R.id.exitButton);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                finish();
            }
        });

        // Enables Always-on
        setAmbientEnabled();
    }
}
