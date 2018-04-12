package com.cross.beaglesight;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;

import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;

import static com.cross.beaglesight.ShowSight.CONFIG_TAG;

public class AddSight extends AppCompatActivity implements View.OnClickListener {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_sight);
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);

        Button button = findViewById(R.id.add_button);
        button.setOnClickListener(this);
    }

    @Override
    public void onClick(View v) {
        EditText nameEntry = findViewById(R.id.name);
        EditText descriptionEntry = findViewById(R.id.description);
        BowManager bowManager = BowManager.getInstance(this);

        String name = nameEntry.getText().toString();
        String description = descriptionEntry.getText().toString();

        BowConfig bowConfig = new BowConfig(name, description);
        bowManager.addBowConfig(bowConfig);

        Intent intent = new Intent(this, ShowSight.class);
        intent.putExtra(CONFIG_TAG, bowConfig.getId());
        startActivity(intent);
    }
}
