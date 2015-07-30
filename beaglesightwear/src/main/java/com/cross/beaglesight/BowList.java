package com.cross.beaglesight;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.support.wearable.view.WearableListView;

import com.cross.beaglesightlibs.BowManager;
import java.util.Vector;


public class BowList extends Activity implements WearableListView.ClickListener {

    private WearableListView mListView;
    private BowManager bm;
    private Vector<String> bowList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        bm = BowManager.getInstance(this);
        bowList = bm.getBowList();


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
