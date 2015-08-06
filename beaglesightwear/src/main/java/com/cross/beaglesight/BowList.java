package com.cross.beaglesight;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.support.wearable.view.WearableListView;
import android.widget.Toast;

import com.cross.beaglesightlibs.BowManager;
import java.util.Vector;


public class BowList extends Activity implements WearableListView.ClickListener {
    private WearableListView mListView;
    private BowManager bm;
    private Vector<String> bowList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        populateBowList();
    }

    private void populateBowList() {
        bm = BowManager.getInstance(this);
        bowList = bm.getBowList();

        if (bowList.size() == 0) {
            Toast.makeText(getApplicationContext(), "Open phone app and add some sight settings first",
                    Toast.LENGTH_LONG).show();
            finish();
        }


        setContentView(R.layout.activity_bow_list);
        mListView = (WearableListView)findViewById(R.id.listView);
        mListView.setAdapter(new BowListAdaptor(this, bowList));
        mListView.setClickListener(this);
    }

    @Override
    public void onClick(WearableListView.ViewHolder viewHolder) {
        Integer num = (Integer)viewHolder.itemView.getTag();
        String bowname = bowList.get(num);
        Intent intent = new Intent(this, ShowBow.class);
        intent.putExtra("bowname", bowname);
        startActivity(intent);
    }

    @Override
    public void onTopEmptyRegionClick() {

    }
}
