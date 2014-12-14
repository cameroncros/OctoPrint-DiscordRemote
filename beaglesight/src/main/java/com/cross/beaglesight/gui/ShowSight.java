package com.cross.beaglesight.gui;

import android.app.ActionBar;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.support.v4.content.FileProvider;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.widget.EditText;
import android.widget.TableLayout;
import android.widget.TableLayout.LayoutParams;
import android.widget.TableRow;
import android.widget.TextView;

import com.androidplot.xy.LineAndPointFormatter;
import com.androidplot.xy.PointLabelFormatter;
import com.androidplot.xy.SimpleXYSeries;
import com.androidplot.xy.XYPlot;
import com.androidplot.xy.XYSeries;
import com.cross.beaglesight.BowManager;
import com.cross.beaglesight.PositionCalculator;
import com.cross.beaglesight.R;

import java.io.File;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;

public class ShowSight extends FragmentActivity
{
	DecimalFormat df = null, hn = null;
	BowManager bm = null;
	PositionCalculator pc = null;

	String bowname = null;
	/** Called when the activity is first created. */
	@Override
	public void onCreate(Bundle savedInstanceState)
	{
		super.onCreate(savedInstanceState);
		setContentView(R.layout.showsight);
        // get action bar
        ActionBar actionBar = getActionBar();
        actionBar.setDisplayHomeAsUpEnabled(true);



	}

    private void drawGraph() {
        XYPlot plot = (XYPlot) findViewById(R.id.showPlot);

        // Create a couple arrays of y-values to plot:
        ArrayList<Integer> distances = new ArrayList<Integer>();
        ArrayList<Double> scopeSettings =  new ArrayList<Double>();
        for (int i = 0; i < 101; i++) {
            distances.add(i);
            scopeSettings.add(pc.calcPosition(i));
        }

        // Turn the above arrays into XYSeries':
        XYSeries series1 = new SimpleXYSeries(distances, scopeSettings, "Scope Settings");

        // Create a formatter to use for drawing a series using LineAndPointRenderer
        // and configure it from xml:
        LineAndPointFormatter series1Format = new LineAndPointFormatter();
        series1Format.setPointLabelFormatter(new PointLabelFormatter());
        series1Format.configure(getApplicationContext(),
                R.xml.line_point_formatter_with_plf1);

        // add a new series' to the xyplot:
        plot.addSeries(series1, series1Format);


        // Create a couple arrays of y-values to plot:
        List<Double> distances2 = pc.getKnownDistances();
        List<Double> scopeSettings2 =  pc.getKnownPositions();


        // Turn the above arrays into XYSeries':
        XYSeries series2 = new SimpleXYSeries(distances2, scopeSettings2, "Known Positions");

        // Create a formatter to use for drawing a series using LineAndPointRenderer
        // and configure it from xml:
        LineAndPointFormatter series2Format = new LineAndPointFormatter();
        series2Format.setPointLabelFormatter(new PointLabelFormatter());
        series2Format.configure(getApplicationContext(),
                R.xml.line_point_formatter_with_plf2);

        // add a new series' to the xyplot:
        plot.addSeries(series2, series2Format);

        // reduce the number of range labels
        plot.setTicksPerRangeLabel(5);
        plot.setTicksPerDomainLabel(10);
        plot.getGraphWidget().setDomainLabelOrientation(-45);
    }

    @Override
	protected void onStart() {
		super.onStart();
		Bundle bundle = getIntent().getExtras();
		bowname = bundle.getString("bowname");
		setTitle(bowname);
		bm = BowManager.getInstance(this.getApplicationContext());
		hn = new DecimalFormat("#");
		df = new DecimalFormat("#.##");
		pc = bm.getPositionCalculator(bowname);
		textListenerSetup();
		calculateIncrements();
        drawGraph();
	};

	@Override
	public boolean onCreateOptionsMenu(Menu menu)
	{
		// TODO: Implement this method
		MenuInflater inf = getMenuInflater();
		inf.inflate(R.menu.show_sight_menu, menu);

        // Return true to display menu
        return super.onCreateOptionsMenu(menu);
    }


    public void shareSettings() {
        // Build Mumble server URL
        File requestFile = new File(bm.getBow(bowname).getPathToFile());
        Context cont = getApplicationContext();
        Uri fileUri = FileProvider.getUriForFile(
                cont,
                "com.cross.beaglesight.fileprovider",
                requestFile);

        Intent intent = new Intent();
        intent.setAction(Intent.ACTION_SEND);
        intent.putExtra(Intent.EXTRA_STREAM, fileUri);
        intent.setType("text/plain");
        startActivity(intent);
    }

	private void calculateIncrements() {
		Double pos = 0.0;
		TableLayout tl = (TableLayout)findViewById(R.id.mainTable);


		Double[] sampleDistances = {10.0, 15.0, 18.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0};
		if(tl.getChildCount() > 0) {
			tl.removeAllViews(); 
		}


		for (Double val : sampleDistances) {
			//TODO highlight known values
			if (pc != null) {
				pos = pc.calcPosition(val);
			}
			TableRow tr = new TableRow(this);
			tr.setLayoutParams(new TableLayout.LayoutParams(LayoutParams.WRAP_CONTENT, LayoutParams.WRAP_CONTENT, 1));

			EditText et = new EditText(this);
			et.setEnabled(false);
			et.setGravity(Gravity.RIGHT);
			et.setText(df.format(pos));

			TextView tv = new TextView(this);
			tv.setLabelFor(et.getId());
			tv.setTextSize(18);
			tv.setText(hn.format(val)+":");

			tr.addView(tv);
			tr.addView(et);
			tl.addView(tr);
		}

		tl.invalidate();
	}

	private void textListenerSetup() {
		EditText et = (EditText)findViewById(R.id.calcDistance);
		et.addTextChangedListener(new TextWatcher() {
			public void afterTextChanged(Editable s) {
				BowManager bm = BowManager.getInstance(null);
				pc = bm.getPositionCalculator(bowname);
				Double pos;
				EditText et = (EditText)findViewById(R.id.calcDistance);
				TextView tv = (TextView)findViewById(R.id.calcPosition);
				try {
					Double dist = Double.valueOf(et.getText().toString());
					pos = pc.calcPosition(dist);
					tv.setText(df.format(pos));
				}
				catch (NumberFormatException e) {
					tv.setText("");
				}

			}

			public void beforeTextChanged(CharSequence s, int a, int b, int c) {}
			public void onTextChanged(CharSequence s, int a, int b, int c) {}

		});
	}

	public boolean onOptionsItemSelected(MenuItem item){
		Intent intent;
		switch (item.getItemId()) {
		case android.R.id.home:
			finish();
			return true;
		case R.id.menu_edit:
			intent = new Intent(getApplicationContext(), AddActivity.class);
			intent.putExtra("bowname", bowname);
			startActivity(intent);
			return true;
		//case R.id.menu_share:
		case R.id.menu_delete:
			bm.deleteBow(bowname);
			intent = new Intent(getApplicationContext(), MainActivity.class);
			startActivityForResult(intent, 0);
			return true;
        case R.id.menu_item_share:
            shareSettings();
            return true;
		default:
			return false;

		}
	}
}
