package com.cross.beaglesight;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.ActionMode;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;

import com.cross.beaglesight.views.SightGraph;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesightlibs.PositionCalculator;
import com.cross.beaglesightlibs.PositionPair;
import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;

public class ShowSight extends AppCompatActivity implements SightGraph.SightGraphCallback {
    static final String CONFIG_TAG = "config";
    private static final int ADD_DISTANCE = 1;
    private SightGraph sightGraph = null;

    private EditText distance;
    private EditText position;

    private String id;
    private BowConfig bowConfig;
    private PositionCalculator positionCalculator;
    private ActionMode actionMode;
    private PositionPair selectedPair;

    private final TextWatcher distanceListener = new TextWatcher() {
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
            id = (String) intent.getSerializableExtra(CONFIG_TAG);
            bowConfig = BowManager.getInstance(this).getBowConfig(id);

            final Intent addDistance = new Intent(this, AddDistance.class);
            addDistance.putExtra(CONFIG_TAG, bowConfig.getId());

            FloatingActionButton fab = findViewById(R.id.fabShowSight);
            fab.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    startActivityForResult(addDistance, ADD_DISTANCE);
                }
            });
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);

            positionCalculator = bowConfig.getPositionCalculator();

            sightGraph = findViewById(R.id.sightGraph);
            sightGraph.setBowConfig(bowConfig);
            sightGraph.setUpdateDistanceCallback(this);
            sightGraph.invalidate();
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
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        switch (requestCode) {
            case ADD_DISTANCE:
                if (resultCode == RESULT_OK)
                {
                    try
                    {
                        bowConfig = BowManager.getInstance(this).getBowConfig(id);
                        sightGraph.setBowConfig(bowConfig);
                        sightGraph.setUpdateDistanceCallback(this);
                        sightGraph.invalidate();
                    }
                    catch (InvalidBowConfigIdException e)
                    {
                        Toast.makeText(this, R.string.failed_find_bow_settings, Toast.LENGTH_LONG).show();
                        finish();
                    }
                }
                break;
        }
    }

    @Override
    public void updateDistance(float distance) {
        this.distance.setText(PositionCalculator.getDisplayValue(distance, 0));
    }

    @Override
    public void setSelected(PositionPair newSelectedPair) {
        // If nothing is selected, end the context menu.
        if (actionMode != null) {
            if (newSelectedPair == null) {
                actionMode.getMenu().findItem(R.id.delete_position).setEnabled(false);
            } else {
                actionMode.getMenu().findItem(R.id.delete_position).setEnabled(true);
            }
        }
        this.selectedPair = newSelectedPair;
    }

    @Override
    public void startDelete()
    {
        actionMode = startActionMode(selectedActionMode);
    }

    private final ActionMode.Callback selectedActionMode = new ActionMode.Callback() {
        @Override
        public boolean onCreateActionMode(ActionMode mode, Menu menu) {
            MenuInflater inflater = mode.getMenuInflater();
            inflater.inflate(R.menu.menu_show_sight_selected, menu);
            return true;
        }

        @Override
        public boolean onPrepareActionMode(ActionMode mode, Menu menu) {
            return false;
        }

        @Override
        public boolean onActionItemClicked(ActionMode mode, MenuItem item) {
            switch (item.getItemId()) {
                case R.id.delete_position:
                    bowConfig.deletePosition(selectedPair);
                    BowManager.getInstance(getBaseContext()).addBowConfig(bowConfig);
                    mode.finish();
                    recreate();
                    break;
            }
            return true;
        }

        @Override
        public void onDestroyActionMode(ActionMode mode) {

        }
    };
}
