package com.cross.beaglesightlibs;

import android.util.Log;

import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.DecompositionSolver;
import org.apache.commons.math3.linear.LUDecomposition;
import org.apache.commons.math3.linear.RealMatrix;
import org.apache.commons.math3.linear.RealVector;

import java.util.List;

public class LineOfBestFitCalculator extends PositionCalculator {
	private int size = 0;
	private int order = 4;
	private RealVector polynomial;

	@Override
	public void setPositions(List<PositionPair> pos) {
		super.setPositions(pos);
		calcPolynomial();
	}

	@Override
	public float calcPosition(float distance) {
	    if (size < 2)
        {
            return Float.NaN;
        }
		double [] val = new double[order];
		for (int j = 0; j < order; j++) {
			val[j]=Math.pow(distance, order-1-j);
		}
		RealVector a = new ArrayRealVector(val);
		return (float)a.dotProduct(polynomial);
	}

	/**
	 * ideas from here: http://www.had2know.com/academics/quadratic-regression-calculator.html
	 */
	private void calcPolynomial() {
		try {
			size = positions.size();
            if (size < 2) {
                return;
            }
			order = size;
			if (order > 4) {
				order = 4;
			}
			double [][] values = new double[order][order];
			double [] rhs = new double[order];
			double [] xsum = new double[2*order-1];

			for (int i = 0; i < order; i++) {
				rhs[i]=sum(positions,order-1-i,1);
				
			}
			for (int i = 0; i < 2*(order-1); i++) {
				xsum[i]=sum(positions,i,0);
			}
			
			for (int i = 0; i < order; i++) {
				for (int j = 0; j < order; j++) {
					values[i][j]=xsum[2*(order-1)-i-j];
				}	
			}
			
			RealMatrix a = new Array2DRowRealMatrix(values);
			
			//Log.e("BeagleSight","a matrix: " + a);
			DecompositionSolver solver = new LUDecomposition(a).getSolver();

			RealVector b = new ArrayRealVector(rhs);
			polynomial = solver.solve(b);
			Log.i("BeagleSight", a.toString());
			Log.i("BeagleSight", b.toString());
			Log.i("BeagleSight", polynomial.toString());
		}

		catch (Exception e) {
			Log.e("Beagle", e.getMessage());
		}
		
	}

	private float sum(List<PositionPair> positionArray, int xpower, int ypower) {
		float val = 0;
		for (PositionPair pair : positionArray) {
			float x = pair.getDistanceFloat();
			float y = pair.getPositionFloat();
			val += Math.pow(x, xpower)*Math.pow(y, ypower);
			
		}
		return val;
	}

	@Override
	public int precision() {
		// TODO Auto-generated method stub
		return 0;
	}

}
