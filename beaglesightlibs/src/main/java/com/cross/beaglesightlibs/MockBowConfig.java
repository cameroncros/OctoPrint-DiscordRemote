package com.cross.beaglesightlibs;

public class MockBowConfig extends BowConfig {
    public MockBowConfig()
    {
        super("MockBowConfig", "Mock Description");
    }

    @Override
    public void initPositionCalculator()
    {
        positionCalculator = new MockPositionCalculator();
    }

    private class MockPositionCalculator extends PositionCalculator {
        @Override
        public float calcPosition(float distance) {
            return -(distance) * (distance - 60) * (distance - 1000) / 60000;
        }
    }
}
