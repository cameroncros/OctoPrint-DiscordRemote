package com.cross.beaglesightlibs;

import android.util.Log;

import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.DecompositionSolver;
import org.apache.commons.math3.linear.LUDecomposition;
import org.apache.commons.math3.linear.RealMatrix;
import org.apache.commons.math3.linear.RealVector;

import java.util.List;
import java.util.Map;

@Deprecated
public class PolynomialCalculator extends PositionCalculator
{
	private RealVector polynomial;
	private int size;

	@Override
	void setPositions(List<PositionPair> pos)
	{
		super.setPositions(pos);
		calcPolynomial();
	}

	public float calcPosition(float distance) {
		if (size < 3) {
			return Float.NaN;
		}
		double [] val = new double[size];
		for (int j = 0; j < size; j++) {
			val[j]=Math.pow(distance, size-j-1);
		}
		RealVector a = new ArrayRealVector(val);
		return (float)a.dotProduct(polynomial);

	}

	private void calcPolynomial() {
		try {
			size = positions.size();
			if (size < 3) {
				return;
			}
			double [][] values = new double[size][size];
			double [] rhs = new double[size];

			int i = 0;
			for (PositionPair pair : positions) {
				double distance = pair.getDistanceFloat();
				double position = pair.getPositionFloat();
				rhs[i]=position;
				for (int j = 0; j < size; j++) {
					values[i][j]=Math.pow(distance, size-j-1);
				}
				i++;
			}

			RealMatrix a = new Array2DRowRealMatrix(values);
			//Log.e("BeagleSight","a matrix: " + a);
			DecompositionSolver solver = new LUDecomposition(a).getSolver();

			RealVector b = new ArrayRealVector(rhs);
			polynomial = solver.solve(b);
			Log.i("BeagleSight", polynomial.toString());
		}

		catch (Exception e) {
			Log.e("Beagle", e.getMessage());
		}
		
	}

	public int precision() {
		switch (positions.size()) {
		case 0:
		case 1:
		case 2:
			return 0;
		default:
			return positions.size()-2;
		}
	}
}
