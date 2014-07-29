package com.cross.beaglesight;

import android.app.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import android.text.*;

public class MainActivity extends Activity
{
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
	{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
		
		EditText et = (EditText)findViewById(R.id.calcDistance);
		et.addTextChangedListener(new TextWatcher() {
			public void afterTextChanged(Editable s) {
				TextView tv = (TextView)findViewById(R.id.calcPosition);
				tv.setText("Hello");
			}
			public void beforeTextChanged(CharSequence s, int a, int b, int c) {}
			public void onTextChanged(CharSequence s, int a, int b, int c) {}
				
		});
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu)
	{
		// TODO: Implement this method
		MenuInflater inf = getMenuInflater();
		inf.inflate(R.menu.menu, menu);
		return super.onCreateOptionsMenu(menu);
	}
}
