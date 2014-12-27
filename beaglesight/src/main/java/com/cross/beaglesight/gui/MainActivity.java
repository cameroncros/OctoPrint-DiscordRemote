package com.cross.beaglesight.gui;

import android.app.FragmentManager;
import android.app.FragmentTransaction;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.v4.app.FragmentActivity;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.LinearLayout;

import com.cross.beaglesightlibs.BowManager;
import com.cross.beaglesight.R;
import com.cross.beaglesight.libs.FloatingActionButton;

import java.io.File;
import java.util.Set;

public class MainActivity extends FragmentActivity
{
    private static final int FILE_SELECT_CODE = 0;

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
    public boolean onCreateOptionsMenu(Menu menu)
    {
        // TODO: Implement this method
        MenuInflater inf = getMenuInflater();
        inf.inflate(R.menu.main_menu, menu);
        return super.onCreateOptionsMenu(menu);
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

    public boolean importBow( MenuItem menuItem ) {
        Intent fileIntent = new Intent(Intent.ACTION_GET_CONTENT);
        fileIntent.setType("file/*"); // intent type to filter application based on your requirement
        startActivityForResult(fileIntent, FILE_SELECT_CODE);
        return false;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        switch (requestCode) {
            case FILE_SELECT_CODE:
                if (resultCode == RESULT_OK) {
                    // Get the Uri of the selected file
                    Uri uri = data.getData();
                    Log.d("BeagleSight", "File Uri: " + uri.toString());
                    // Get the path

                    File fname = new File(getRealPathFromURI(uri));
                    bm.importBow(fname);
                    // Get the file instance
                    // File file = new File(path);
                    // Initiate the upload
                }
                break;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    private String getRealPathFromURI(Uri contentURI) {
        String result;
        Cursor cursor = getContentResolver().query(contentURI, null, null, null, null);
        if (cursor == null) { // Source is Dropbox or other similar local file path
            result = contentURI.getPath();
        } else {
            cursor.moveToFirst();
            int idx = cursor.getColumnIndex(MediaStore.Images.ImageColumns.DATA);
            result = cursor.getString(idx);
            cursor.close();
        }
        return result;
    }

}
