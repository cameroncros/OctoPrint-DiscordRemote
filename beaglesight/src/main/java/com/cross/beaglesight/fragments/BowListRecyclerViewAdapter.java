package com.cross.beaglesight.fragments;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.TextView;

import com.cross.beaglesight.R;
import com.cross.beaglesight.fragments.BowListItemFragment.OnListFragmentInteractionListener;
import com.cross.beaglesightlibs.BowConfig;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link BowConfig} and makes a call to the
 * specified {@link OnListFragmentInteractionListener}.
 */
public class BowListRecyclerViewAdapter extends RecyclerView.Adapter<BowListRecyclerViewAdapter.ViewHolder> {

    private final List<BowConfig> mValues;
    private final OnListFragmentInteractionListener mListener;

    public BowListRecyclerViewAdapter(List<BowConfig> items, OnListFragmentInteractionListener listener) {
        mValues = items;
        mListener = listener;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.fragment_bowlist_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.mIdView.setText(mValues.get(position).getName());
        holder.mContentView.setText(mValues.get(position).getDescription());

        holder.mView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (null != mListener) {
                    // Notify the active callbacks interface (the activity, if the
                    // fragment is attached to one) that an item has been selected.
                    mListener.onListFragmentInteraction(holder.mItem);
                }
            }
        });
    }

    @Override
    public int getItemCount() {
        return mValues.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        final View mView;
        final TextView mIdView;
        final TextView mContentView;
        final CheckBox mSelectView;
        BowConfig mItem;

        ViewHolder(View view) {
            super(view);
            mView = view;
            mIdView = view.findViewById(R.id.itemName);
            mContentView = view.findViewById(R.id.itemDescription);
            mSelectView = view.findViewById(R.id.itemSelect);
            mSelectView.setVisibility(View.INVISIBLE);
        }

        @Override
        public String toString() {
            return super.toString() + " '" + mContentView.getText() + "'";
        }
    }
}
