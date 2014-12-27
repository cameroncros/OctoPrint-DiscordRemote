package com.cross.beaglesightlibs;

import android.util.Log;

import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.DecompositionSolver;
import org.apache.commons.math3.linear.LUDecomposition;
import org.apache.commons.math3.linear.RealMatrix;
import org.apache.commons.math3.linear.RealVector;

import java.util.HashMap;
import java.util.Map;

public class LineOfBestFitCalculator extends PositionCalculator {
	int size = 0;
	int order = 0;
	RealVector polynomial;
	
	LineOfBestFitCalculator(int order) {
		this.order = order;
		positionArray = new HashMap<Double,Double>();
	}

	@Override
	public void setPositions(Map<String, String> pos) {
		super.setPositions(pos);
		calcPolynomial();
	}

	@Override
	public double calcPosition(double distance) {
		if (size < order) {
			return Double.NaN;
		}
		double [] val = new double[order];
		for (int j = 0; j < order; j++) {
			val[j]=Math.pow(distance, order-1-j);
		}
		RealVector a = new ArrayRealVector(val);
		return a.dotProduct(polynomial);
	}

	/**
	 * ideas from here: http://www.had2know.com/academics/quadratic-regression-calculator.html
	 */
	void calcPolynomial() {
		try {
			size = positionArray.size();
			if (size < order) {
				return;
			}
			double [][] values = new double[order][order];
			double [] rhs = new double[order];
			double [] xsum = new double[2*order-1];

			for (int i = 0; i < order; i++) {
				rhs[i]=sum(positionArray,order-1-i,1);
				
			}
			for (int i = 0; i < 2*(order-1); i++) {
				xsum[i]=sum(positionArray,i,0);
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

	private double sum(Map<Double, Double> positionArray, int xpower, int ypower) {
		double val = 0;
		for (Double x : positionArray.keySet()) {
			double y = positionArray.get(x);
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
