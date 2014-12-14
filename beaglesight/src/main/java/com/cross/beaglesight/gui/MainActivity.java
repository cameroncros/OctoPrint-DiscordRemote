package com.cross.beaglesight.gui;

import android.app.FragmentManager;
import android.app.FragmentTransaction;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.support.v4.app.FragmentActivity;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;

import com.cross.beaglesight.BowManager;
import com.cross.beaglesight.R;
import com.cross.beaglesight.gui.libs.FloatingActionButton;

import java.util.Set;

public class MainActivity extends FragmentActivity
{
	BowManager bm = null;
    public Context context = null;
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
	{
        this.context = getApplicationContext();
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        
        bm = BowManager.getInstance(this.getApplicationContext());

        FloatingActionButton fabButton = new FloatingActionButton.Builder(this)
                .withDrawable(getResources().getDrawable(R.drawable.ic_action_new))
                .withButtonColor(Color.WHITE)
                .withGravity(Gravity.BOTTOM | Gravity.RIGHT)
                .withMargins(0, 0, 16, 16)
                .create();
        fabButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                addNewBow();
            }
        });
        fillBowList();   
    }
    
    @Override
	protected void onStart() {
    	super.onStart();
    	fillBowList();  
    };

    
    
    
    
    void fillBowList() {
    	BowManager bm = BowManager.getInstance(this.getApplicationContext());

        LinearLayout lv = (LinearLayout) findViewById(R.id.bowList);
    	lv.removeAllViews(); 
    	FragmentManager fragmentManager = getFragmentManager();
    	
    	

		Set<String> bows = bm.getBowList();

		for (String bowname : bows) {
			 
			FragmentTransaction fragmentTransaction = fragmentManager.beginTransaction();
            bowlistFragment hello = new bowlistFragment();
           
            fragmentTransaction.add(R.id.bowList, hello, bowname);
            fragmentTransaction.commit();
            hello.setText(bowname);
		
		}

		lv.invalidate();
	
	}
    

	
	


	
	public boolean addNewBow() {
		Intent intent = new Intent(this, AddActivity.class);
		startActivity(intent);
		return false;
	}
}
