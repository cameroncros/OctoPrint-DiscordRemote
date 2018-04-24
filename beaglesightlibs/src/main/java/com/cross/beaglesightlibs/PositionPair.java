package com.cross.beaglesightlibs;

import com.cross.beaglesightlibs.exceptions.InvalidNumberFormatException;

public class PositionPair {
    private String positionString;
    private String distanceString;
    private float positionFloat;
    private float distanceFloat;

    public PositionPair(float distance, float position)
    {
        distanceFloat = distance;
        positionFloat = position;

        distanceString = Float.toString(distance);
        positionString = Float.toString(position);
    }

    public PositionPair(String distance, String position) throws InvalidNumberFormatException
    {
        distanceString = distance;
        positionString = position;
        try
        {
            distanceFloat = Float.parseFloat(distance);
            positionFloat = Float.parseFloat(position);
        }
        catch (NumberFormatException nfe)
        {
            throw new InvalidNumberFormatException(nfe);
        }
    }

    public String getDistanceString() {
        return distanceString;
    }

    public String getPositionString() {
        return positionString;
    }

    public float getDistanceFloat() {
        return distanceFloat;
    }

    public float getPositionFloat() {
        return positionFloat;
    }

    @Override
    public String toString()
    {
        return distanceString + "," + positionString;
    }
}
