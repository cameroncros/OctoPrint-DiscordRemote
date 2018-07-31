package com.cross.beaglesight.fragments;

import android.support.v7.widget.RecyclerView;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.TextView;

import com.cross.beaglesight.R;
import com.cross.beaglesightlibs.BowConfig;

import java.util.List;

/**
 * {@link RecyclerView.Adapter} that can display a {@link BowConfig} and makes a call to the
 * specified {@link OnListFragmentInteractionListener}.
 */
public class BowListRecyclerViewAdapter extends RecyclerView.Adapter<BowListRecyclerViewAdapter.ViewHolder> {

    private final List<BowConfig> mValues;
    private final OnListFragmentInteractionListener mListener;
    private Boolean multiSelect = false;

    public BowListRecyclerViewAdapter(List<BowConfig> items, OnListFragmentInteractionListener listener) {
        mValues = items;
        mListener = listener;
    }

    @Override
    public ViewHolder onCreateViewHolder(ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.bowlist_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(final ViewHolder holder, int position) {
        holder.mItem = mValues.get(position);
        holder.mNameView.setText(mValues.get(position).getName());
        holder.mDescriptionView.setText(mValues.get(position).getDescription());
        if (multiSelect) {
            holder.mSelectView.setVisibility(View.VISIBLE);
        } else {
            holder.mSelectView.setVisibility(View.INVISIBLE);
        }

        holder.mView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mListener != null) {
                    Boolean selected = mListener.onListFragmentInteraction(holder.mItem);
                    CheckBox checkBox = v.findViewById(R.id.itemSelect);
                    checkBox.setChecked(selected);
                    checkBox.invalidate();
                }
            }
        });

        holder.mView.setOnLongClickListener(new View.OnLongClickListener() {

            @Override
            public boolean onLongClick(View v) {
                if (mListener != null) {
                    CheckBox checkBox = holder.mView.findViewById(R.id.itemSelect);
                    checkBox.setSelected(true);
                    mListener.onListFragmentLongPress(holder.mItem);
                    holder.mSelectView.setSelected(true);
                }
                return true;
            }
        });
    }

    @Override
    public int getItemCount() {
        return mValues.size();
    }

    public void enableMultiSelectMode(Boolean enabled) {
        multiSelect = enabled;
        notifyDataSetChanged();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        final View mView;
        final TextView mNameView;
        final TextView mDescriptionView;
        final CheckBox mSelectView;
        BowConfig mItem;

        ViewHolder(View view) {
            super(view);
            mView = view;
            mNameView = view.findViewById(R.id.itemName);
            mDescriptionView = view.findViewById(R.id.itemDescription);
            mSelectView = view.findViewById(R.id.itemSelect);
            mSelectView.setVisibility(View.INVISIBLE);
        }

        @Override
        public String toString() {
            return super.toString() + " '" + mDescriptionView.getText() + "'";
        }
    }

    /**
     * This interface must be implemented by activities that contain this
     * fragment to allow an interaction in this fragment to be communicated
     * to the activity and potentially other fragments contained in that
     * activity.
     * <p/>
     * See the Android Training lesson <a href=
     * "http://developer.android.com/training/basics/fragments/communicating.html"
     * >Communicating with Other Fragments</a> for more information.
     */
    public interface OnListFragmentInteractionListener {
        // TODO: Update argument type and name
        Boolean onListFragmentInteraction(BowConfig item);
        void onListFragmentLongPress(BowConfig item);
    }
}


