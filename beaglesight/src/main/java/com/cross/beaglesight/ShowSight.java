package com.cross.beaglesight;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import com.cross.beaglesight.views.SightGraph;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesightlibs.PositionCalculator;
import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;

public class ShowSight extends AppCompatActivity implements SightGraph.SightGraphCallback {
    static final String CONFIG_TAG = "config";
    SightGraph sightGraph = null;

    EditText distance;
    EditText position;

    private PositionCalculator positionCalculator;

    private TextWatcher distanceListener = new TextWatcher() {
        @Override
        public void beforeTextChanged(CharSequence s, int start, int count, int after) {

        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {

        }

        @Override
        public void afterTextChanged(Editable s) {
            try {
                float dist = Float.parseFloat(s.toString());
                float posVal = positionCalculator.calcPosition(dist);
                String posStr = PositionCalculator.getDisplayValue(posVal, 2);
                position.setText(posStr);
                sightGraph.setSelectedDistance(dist);
            }
            catch (NumberFormatException nfe)
            {
                // Do nothing.
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        try {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_show_sight);
            Toolbar toolbar = findViewById(R.id.toolbar);
            setSupportActionBar(toolbar);

            Intent intent = getIntent();
            String id = (String) intent.getSerializableExtra(CONFIG_TAG);
            BowConfig bowConfig = BowManager.getInstance(this).getBowConfig(id);;

            final Intent addDistance = new Intent(this, AddDistance.class);
            addDistance.putExtra(CONFIG_TAG, bowConfig.getId());

            FloatingActionButton fab = findViewById(R.id.fabShowSight);
            fab.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    startActivity(addDistance);
                }
            });
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);

            sightGraph = findViewById(R.id.sightGraph);
            sightGraph.setBowConfig(bowConfig);
            sightGraph.setUpdateDistanceCallback(this);
            sightGraph.invalidate();

            positionCalculator = bowConfig.getPositionCalculator();

            distance = findViewById(R.id.distanceText);
            position = findViewById(R.id.positionText);
            distance.addTextChangedListener(distanceListener);
        }
        catch (InvalidBowConfigIdException e)
        {
            Toast.makeText(this, R.string.failed_find_bow_settings, Toast.LENGTH_LONG).show();
            finish();
        }
    }

    @Override
    public void updateDistance(float distance) {
        this.distance.setText(PositionCalculator.getDisplayValue(distance, 0));
    }
}
