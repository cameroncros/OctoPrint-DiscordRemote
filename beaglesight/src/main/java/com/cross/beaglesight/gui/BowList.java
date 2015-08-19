package com.cross.beaglesight.gui;

import android.app.Activity;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.v4.widget.SwipeRefreshLayout;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.util.Log;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;

import com.cross.beaglesight.R;
import com.cross.beaglesight.libs.FloatingActionButton;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;

import java.io.File;

public class BowList extends Activity {
    private static final int FILE_SELECT_CODE = 0;
    BowManager bm = null;

    private RecyclerView mRecyclerView;
    private BowListAdapter mAdapter;
    private RecyclerView.LayoutManager mLayoutManager;

    /**
     * Called when the activity is first created.
     */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.bowlist);

        bm = BowManager.getInstance(this.getApplicationContext());

        mRecyclerView = (RecyclerView) findViewById(R.id.my_recycler_view);

        // use this setting to improve performance if you know that changes
        // in content do not change the layout size of the RecyclerView
        mRecyclerView.setHasFixedSize(true);

        // use a linear layout manager
        mLayoutManager = new LinearLayoutManager(this);
        mRecyclerView.setLayoutManager(mLayoutManager);


        mAdapter = new BowListAdapter(this, bm.getBowList());
        mRecyclerView.setAdapter(mAdapter);


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

    }

    @Override
    protected void onStart() {
        super.onStart();
        mAdapter.setData(bm.getBowList());
        mAdapter.notifyDataSetChanged();
    }

    @Override
    protected void onResume() {
        super.onResume();
        mAdapter.setData(bm.getBowList());
        mAdapter.notifyDataSetChanged();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // TODO: Implement this method
        MenuInflater inf = getMenuInflater();
        inf.inflate(R.menu.main_menu, menu);
        return super.onCreateOptionsMenu(menu);
    }

    public boolean addNewBow() {
        Intent intent = new Intent(this, AddActivity.class);
        startActivity(intent);
        return false;
    }

    public boolean importBow(MenuItem menuItem) {
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
                    BowConfig bc = bm.importBow(fname);
                    if (bc != null) {
                        bm.saveBowConfig(bc);
                        //todo add message if it fails to load
                    }
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
