package com.cross.beaglesight;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesightlibs.PositionCalculator;
import com.cross.beaglesightlibs.PositionPair;
import com.cross.beaglesightlibs.exceptions.InvalidBowConfigIdException;
import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException;

import static com.cross.beaglesight.ShowSight.CONFIG_TAG;

public class AddDistance extends AppCompatActivity {

    private Button add = null;

    private EditText simpleDistance = null;
    private EditText simplePin = null;

    private EditText pinSetting1 = null;
    private EditText offset1 = null;

    private EditText pinSetting2 = null;
    private EditText offset2 = null;

    private BowManager bowManager = null;
    private BowConfig bowConfig = null;


    private void updateAddStatus()
    {
        String distance = simpleDistance.getText().toString();
        String pinSetting = simplePin.getText().toString();

        try {
            //noinspection ResultOfMethodCallIgnored
            Double.parseDouble(distance);
            //noinspection ResultOfMethodCallIgnored
            Double.parseDouble(pinSetting);
            add.setEnabled(true);
            add.invalidate();
        }
        catch (NumberFormatException nfe)
        {
            add.setEnabled(false);
            add.invalidate();
        }
    }

    private void calculateResultPin()
    {
        if (!simpleDistance.getText().toString().equals(""))
        {
            return;
        }
        try {
            float y1 = Float.parseFloat(pinSetting1.getText().toString());
            float y2 = Float.parseFloat(pinSetting2.getText().toString());
            float x1 = Float.parseFloat(offset1.getText().toString());
            float x2 = Float.parseFloat(offset2.getText().toString());

            // y(0) == Correct pin setting
            //y(x) = (y1-y2)/(x1-x2) * x + c
            // y(0) = c
            // c = y1 - (y1-y2)/(x1-x2) * x1
            float c = y1 - ((y1-y2)/(x1-x2) * x1);
            String cstring = PositionCalculator.getDisplayValue(c, 2);

            if (simplePin.getText().toString().equals(""))
            {
                simplePin.setText(cstring);
            }
        }
        catch (NumberFormatException nfe) {
            // Do nothing
        }
    }

    private void updateEstimates()
    {
        String distance = simpleDistance.getText().toString();
        try {
            float dist = Float.parseFloat(distance);
            // Guess first pin setting.
            {
                float positionGuess = bowConfig.getPositionCalculator().calcPosition(dist);
                if (positionGuess == Float.NaN) {
                    return;
                }
                String guessString = PositionCalculator.getDisplayValue(positionGuess, 0);
                if (offset1.getText().toString().equals("")) {
                    pinSetting1.setText(guessString);
                }
            }
            // Guess slightly offsetted pin setting.
            {
                float positionGuess = bowConfig.getPositionCalculator().calcPosition(dist-1);
                if (positionGuess == Float.NaN) {
                    return;
                }
                String guessString = PositionCalculator.getDisplayValue(positionGuess, 0);
                if (offset2.getText().toString().equals("")) {
                    pinSetting2.setText(guessString);
                }
            }

        }
        catch (NumberFormatException nfe)
        {
            // Do nothing.
        }
    }

    private final TextWatcher simpleListener = new TextWatcher() {

        @Override
        public void beforeTextChanged(CharSequence s, int start, int count, int after) {

        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {

        }

        @Override
        public void afterTextChanged(Editable s) {
            updateAddStatus();
            updateEstimates();

        }
    };

    private final TextWatcher calcPinListener = new TextWatcher() {

        @Override
        public void beforeTextChanged(CharSequence s, int start, int count, int after) {

        }

        @Override
        public void onTextChanged(CharSequence s, int start, int before, int count) {

        }

        @Override
        public void afterTextChanged(Editable s) {
            calculateResultPin();
        }
    };

    private final View.OnClickListener addPinSetting = new View.OnClickListener() {

        @SuppressWarnings("ResultOfMethodCallIgnored")
        @Override
        public void onClick(View v) {
            String distance = simpleDistance.getText().toString();
            String pinSetting = simplePin.getText().toString();

            try {
                Double.parseDouble(distance);
                Double.parseDouble(pinSetting);

                try {
                    bowConfig.addPosition(new PositionPair(distance, pinSetting));
                }
                catch (InvalidNumberFormatException e)
                {
                    // Ignore, should never happen
                }
                bowManager.addBowConfig(bowConfig);

                Intent intent = new Intent();
                setResult(RESULT_OK, intent);
                finish();
            }
            catch (NumberFormatException nfe)
            {
                add.setEnabled(false);
            }
        }
    };


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_distance);
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);


        Intent intent = getIntent();
        String id = (String) intent.getSerializableExtra(CONFIG_TAG);
        try {
            bowManager = BowManager.getInstance(this);
            bowConfig = bowManager.getBowConfig(id);
        }
        catch (InvalidBowConfigIdException e)
        {
            Toast.makeText(this, R.string.failed_find_bow_settings, Toast.LENGTH_LONG).show();
            finish();
        }

        add = findViewById(R.id.addDistance);
        add.setOnClickListener(addPinSetting);
        add.setEnabled(false);

        simpleDistance = findViewById(R.id.simpleDistance);
        simplePin = findViewById(R.id.simplePin);

        simpleDistance.addTextChangedListener(simpleListener);
        simplePin.addTextChangedListener(simpleListener);

        pinSetting1 = findViewById(R.id.pinSetting1);
        pinSetting2 = findViewById(R.id.pinSetting2);
        offset1 = findViewById(R.id.offset1);
        offset2 = findViewById(R.id.offset2);

        pinSetting1.addTextChangedListener(calcPinListener);
        pinSetting2.addTextChangedListener(calcPinListener);
        offset1.addTextChangedListener(calcPinListener);
        offset2.addTextChangedListener(calcPinListener);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                Intent intent = new Intent();
                setResult(RESULT_CANCELED, intent);
                finish();
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }
}
