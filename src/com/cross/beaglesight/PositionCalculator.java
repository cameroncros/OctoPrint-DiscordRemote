package com.cross.beaglesight;

import java.util.HashMap;
import java.util.Map;
import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.DecompositionSolver;
import org.apache.commons.math3.linear.LUDecomposition;
import org.apache.commons.math3.linear.RealMatrix;
import org.apache.commons.math3.linear.RealVector;

import android.util.Log;

import com.cross.beaglesight.BowConfig.KnownPosition;

public class PositionCalculator
{

	Map<String,KnownPosition> positionArray = null;
	RealVector polynomial;
	int size;

	PositionCalculator() {
		positionArray = new HashMap<String,KnownPosition>();
	}

	void setPositions(Map<String,KnownPosition> pos) 
	{
		positionArray = pos;
		calcPolynomial();
	}

	public double calcPosition(double distance) {
		if (size < 3) {
			return Double.NaN;
		}
		double [] val = new double[size];
		for (int j = 0; j < size; j++) {
			val[j]=Math.pow(distance, size-j-1);
		}
		RealVector a = new ArrayRealVector(val);
		return a.dotProduct(polynomial);

	}

	void calcPolynomial() {
		try {
			size = positionArray.size();
			if (size < 3) {
				return;
			}
			double [][] values = new double[size][size];
			double [] rhs = new double[size];

			int i = 0;
			for (KnownPosition kp : positionArray.values()) {
				rhs[i]=Double.valueOf(kp.Position);
				for (int j = 0; j < size; j++) {
					values[i][j]=Math.pow(Double.valueOf(kp.Distance), size-j-1);
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

	int precision() {
		switch (positionArray.size()) {
		case 0:
		case 1:
		case 2:
			return 0;
		default:
			return positionArray.size()-2;
		}
	}
}
