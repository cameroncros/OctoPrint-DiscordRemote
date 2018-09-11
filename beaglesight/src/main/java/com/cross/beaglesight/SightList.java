package com.cross.beaglesight;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.support.annotation.NonNull;
import android.support.design.widget.AppBarLayout;
import android.support.design.widget.CoordinatorLayout;
import android.support.design.widget.FloatingActionButton;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.LinearLayoutManager;
import android.support.v7.widget.RecyclerView;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.ActionMode;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;

import com.cross.beaglesight.fragments.BowListRecyclerViewAdapter;
import com.cross.beaglesightlibs.BowConfig;
import com.cross.beaglesightlibs.BowManager;

import org.xml.sax.SAXException;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.ParserConfigurationException;

import static com.cross.beaglesight.ShowSight.CONFIG_TAG;

public class SightList extends AppCompatActivity implements BowListRecyclerViewAdapter.OnListFragmentInteractionListener {
    private Intent addIntent;
    private List<BowConfig> configList;
    private ArrayList<BowConfig> selectedBowConfigs;
    private FloatingActionButton fab;

    private static final int FILE_SELECT_CODE = 0;
    private static final int MY_PERMISSIONS_REQUEST_READ_EXTERNAL_STORAGE = 1;
    private BowListRecyclerViewAdapter adapter;
    private AppBarLayout appBarLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sight_list);
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        appBarLayout = findViewById(R.id.app_bar);

        addIntent = new Intent(this, AddSight.class);

        fab = findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                startActivity(addIntent);
            }
        });

        RecyclerView view = findViewById(R.id.bowlistrecyclerview);
        // Set the adapter
        if (view != null) {
            Context context = view.getContext();
            view.setLayoutManager(new LinearLayoutManager(context));
            configList = BowManager.getInstance(getApplicationContext()).getBowList();
            adapter = new BowListRecyclerViewAdapter(configList, this);
            view.setAdapter(adapter);
        }

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_sight_list, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        switch (id)
        {
            case R.id.action_add:
                startActivity(addIntent);
                return true;
            case R.id.action_import:
                if (ContextCompat.checkSelfPermission(this,
                        Manifest.permission.READ_EXTERNAL_STORAGE)
                        != PackageManager.PERMISSION_GRANTED) {

                    // Permission is not granted
                    // Should we show an explanation?
                    if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                            Manifest.permission.READ_EXTERNAL_STORAGE)) {

                        // Show an explanation to the user *asynchronously* -- don't block
                        // this thread waiting for the user's response! After the user
                        // sees the explanation, try again to request the permission.

                    } else {

                        // No explanation needed; request the permission
                        ActivityCompat.requestPermissions(this,
                                new String[]{Manifest.permission.READ_EXTERNAL_STORAGE},
                                MY_PERMISSIONS_REQUEST_READ_EXTERNAL_STORAGE);

                        // MY_PERMISSIONS_REQUEST_READ_CONTACTS is an
                        // app-defined int constant. The callback method gets the
                        // result of the request.
                    }
                } else {
                    importConfig();
                }
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String permissions[], @NonNull int[] grantResults) {
        switch (requestCode) {
            case MY_PERMISSIONS_REQUEST_READ_EXTERNAL_STORAGE: {
                // If request is cancelled, the result arrays are empty.
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED) {

                    // permission was granted, yay! Do the
                    importConfig();
                }
            }
        }
    }

    @Override
    public boolean onListFragmentInteraction(BowConfig bowConfig) {
        if (selectedBowConfigs != null)
        {
            if (selectedBowConfigs.contains(bowConfig))
            {
                selectedBowConfigs.remove(bowConfig);
                return false;
            }
            else
            {
                selectedBowConfigs.add(bowConfig);
                return true;
            }
        }
        else {
            Intent intent = new Intent(this, ShowSight.class);
            intent.putExtra(CONFIG_TAG, bowConfig.getId());
            startActivity(intent);
            return false;
        }
    }

    @SuppressLint("RestrictedApi")
    @Override
    public boolean onListFragmentLongPress(BowConfig bowConfig) {
        if (selectedBowConfigs == null) {
            selectedBowConfigs = new ArrayList<>();
            //TODO: Fix selecting on long press: selectedBowConfigs.add(bowConfig);

            startActionMode(selectedActionMode);

            fab.setVisibility(View.GONE);
            fab.invalidate();

            CoordinatorLayout.LayoutParams lp = (CoordinatorLayout.LayoutParams) appBarLayout.getLayoutParams();
            lp.height = (int) getResources().getDimension(R.dimen.toolbar_height);
            return true;
        }
        return false;
    }

    private final ActionMode.Callback selectedActionMode = new ActionMode.Callback() {
        @Override
        public boolean onCreateActionMode(ActionMode mode, Menu menu) {
            MenuInflater inflater = mode.getMenuInflater();
            inflater.inflate(R.menu.menu_sight_list_selected, menu);

            adapter.enableMultiSelectMode(true);
            adapter.notifyDataSetChanged();
            return true;
        }

        @Override
        public boolean onPrepareActionMode(ActionMode mode, Menu menu) {
            return false;
        }

        @Override
        public boolean onActionItemClicked(ActionMode mode, MenuItem item) {
            BowManager bm = BowManager.getInstance(getBaseContext());
            switch (item.getItemId()) {
                case R.id.action_delete:
                    for (BowConfig config : selectedBowConfigs)
                    {
                        bm.deleteBowConfig(config.getId());
                    }
                    configList.clear();
                    configList.addAll(BowManager.getInstance(getApplicationContext()).getBowList());
                    adapter.notifyDataSetChanged();
                    break;
                case R.id.action_export:
                    File outputDir = getCacheDir();
                    Intent shareIntent = new Intent(Intent.ACTION_SEND_MULTIPLE);
                    shareIntent.setType("text/xml");
                    ArrayList<Uri> uris = new ArrayList<>();

                    for (BowConfig config : selectedBowConfigs)
                    {
                        try {
                            String filename = config.getName();
                            if (filename.length() == 0) {
                                filename = config.getId();
                            }
                            File outputFile = File.createTempFile("BowConfig_" + filename, ".xml", outputDir);
                            FileOutputStream fos = new FileOutputStream(outputFile);
                            config.save(fos);
                            Uri uri = FileProvider.getUriForFile(getApplicationContext(), BuildConfig.APPLICATION_ID, outputFile);
                            uris.add(uri);

                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                    shareIntent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris);
                    startActivity(Intent.createChooser(shareIntent, "Export Configs"));
                    break;
            }
            selectedBowConfigs = null;
            mode.finish();
            return true;
        }

        @SuppressLint("RestrictedApi")
        @Override
        public void onDestroyActionMode(ActionMode mode) {
            adapter.enableMultiSelectMode(false);

            fab.setVisibility(View.VISIBLE);
            fab.invalidate();

            CoordinatorLayout.LayoutParams lp = (CoordinatorLayout.LayoutParams)appBarLayout.getLayoutParams();
            lp.height = (int) getResources().getDimension(R.dimen.app_bar_height);

            selectedBowConfigs = null;
        }
    };

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        switch (requestCode) {
            case FILE_SELECT_CODE:
                if (resultCode == RESULT_OK) {
                    // Get the Uri of the selected file
                    try {
                        Uri uri = data.getData();

                        Log.d("BeagleSight", "File Uri: " + uri.toString());
                        // Get the path

                        File fname = new File(getRealPathFromURI(uri));

                        FileInputStream fis = new FileInputStream(fname);
                        BowConfig bowConfig = new BowConfig(fis);
                        BowManager.getInstance(getApplicationContext()).addBowConfig(bowConfig);
                    } catch (SAXException | ParserConfigurationException | IOException | NullPointerException e) {
                        Toast.makeText(this, "Failed to load BowConfig: " + e.getMessage(), Toast.LENGTH_LONG).show();
                    }
                }
                recreate();
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

    private void importConfig() {
        Intent fileIntent = new Intent(Intent.ACTION_GET_CONTENT);
        fileIntent.setType("file/*"); // intent type to filter application based on your requirement
        startActivityForResult(fileIntent, FILE_SELECT_CODE);
    }
}
