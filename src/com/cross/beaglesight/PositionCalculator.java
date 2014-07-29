package com.cross.beaglesight;

import java.util.HashMap;
import java.util.Map;
import org.apache.commons.math3.linear.Array2DRowRealMatrix;
import org.apache.commons.math3.linear.ArrayRealVector;
import org.apache.commons.math3.linear.DecompositionSolver;
import org.apache.commons.math3.linear.LUDecomposition;
import org.apache.commons.math3.linear.RealMatrix;
import org.apache.commons.math3.linear.RealVector;

public class PositionCalculator
{
	class KnownPosition {
		double Distance;
		double Position;
		KnownPosition(double d, double p) {
			Distance=d;
			Position=p;
		}
	}
	
	Map<Double,KnownPosition> positionArray = null;
	RealVector polynomial;
	int size;
	
	PositionCalculator() {
		positionArray = new HashMap<Double,KnownPosition>();
	}
	
	Boolean addPosition(double distance, double position) 
	{
		if (positionArray.containsKey(distance)) {
			return false;
		}
		positionArray.put(distance, new KnownPosition(distance, position));
		return true;
	}
	
	double calcPosition(double distance) {
		double [] val = new double[size];
		for (int j = size-1; j >= 0; j--) {
			val[size-j]=Math.pow(distance, j);
		}
		RealVector a = new ArrayRealVector(val);
		return a.dotProduct(polynomial);
		
	}
	
	void calcPolynomial() {
		size = positionArray.size();
		double [][] values = new double[size][size];
		double [] rhs = new double[size];
		
		int i = 0;
		for (KnownPosition kp : positionArray.values()) {
			rhs[i]=kp.Position;
			for (int j = size-1; j >= 0; j--) {
				values[i][size-j]=Math.pow(kp.Distance, j);
			}
		}
		
		RealMatrix a = new Array2DRowRealMatrix(values);
        System.out.println("a matrix: " + a);
        DecompositionSolver solver = new LUDecomposition(a).getSolver();

        RealVector b = new ArrayRealVector(rhs);
        polynomial = solver.solve(b);
		
		/*
		double [][] values = {{1, 1, 2}, {2, 4, -3}, {3, 6, -5}};
        double [] rhs = { 9, 1, 0 };

        RealMatrix a = new Array2DRowRealMatrix(values);
        System.out.println("a matrix: " + a);
        DecompositionSolver solver = new LUDecomposition(a).getSolver();

        RealVector b = new ArrayRealVector(rhs);
        RealVector x = solver.solve(b);
        System.out.println("solution x: " + x);;
        RealVector residual = a.operate(x).subtract(b);
        double rnorm = residual.getLInfNorm();
        System.out.println("residual: " + rnorm);
		*/
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
