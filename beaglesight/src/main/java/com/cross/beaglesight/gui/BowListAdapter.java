package com.cross.beaglesight.gui;

import android.content.Context;
import android.content.Intent;
import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.cross.beaglesight.R;
import com.cross.beaglesightlibs.BowManager;

import java.util.Vector;

/**
 * Created by cameron on 8/7/15.
 */
public class BowListAdapter extends RecyclerView.Adapter<BowListAdapter.ViewHolder> {
    private BowManager bm = null;
    private Vector<String> mDataset;
    private Context context;

    // Provide a reference to the views for each data item
    // Complex data items may need more than one view per item, and
    // you provide access to all the views for a data item in a view holder
    public static class ViewHolder extends RecyclerView.ViewHolder {
        // each data item is just a string in this case
        public View view;
        public TextView mBowNameView;
        public TextView mBowDescriptionView;

        public ViewHolder(View v) {
            super(v);
            view = v;
            mBowNameView = (TextView) v.findViewById(R.id.bowname);
            mBowDescriptionView = (TextView) v.findViewById(R.id.bowdescription);
        }
    }

    void setData(Vector<String> myDataSet) {
        mDataset = myDataSet;
    }

    // Provide a suitable constructor (depends on the kind of dataset)
    public BowListAdapter(Context cont, Vector<String> myDataset) {
        mDataset = myDataset;
        context = cont;
        bm = BowManager.getInstance(cont);
    }

    // Create new views (invoked by the layout manager)
    @Override
    public BowListAdapter.ViewHolder onCreateViewHolder(ViewGroup parent,
                                                        int viewType) {
        // create a new view
        View v = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.bow_list_fragment, parent, false);

        // set the view's size, margins, paddings and layout parameters
        ViewHolder vh = new ViewHolder(v);
        return vh;
    }

    // Replace the contents of a view (invoked by the layout manager)
    @Override
    public void onBindViewHolder(ViewHolder holder, int position) {
        // - get element from your dataset at this position
        // - replace the contents of the view with that element
        final String bowname = mDataset.get(position);
        holder.mBowNameView.setText(bowname);
        holder.mBowDescriptionView.setText(bm.getBow(bowname).getDescription());
        holder.view.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(context, ShowSight.class);
                intent.putExtra("bowname", bowname);
                context.startActivity(intent);
            }
        });

    }

    // Return the size of your dataset (invoked by the layout manager)
    @Override
    public int getItemCount() {
        return mDataset.size();
    }


}
