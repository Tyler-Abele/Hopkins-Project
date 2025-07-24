// App.js
import * as React from 'react';
import { NavigationContainer } from '@react-navigation/native';
// IMPORTANT CHANGE: Import from @react-navigation/stack instead of -native-stack
import { createStackNavigator } from '@react-navigation/stack';

// Import your screen components
import HomeScreen from './screens/HomeScreen';
import DetailsScreen from './screens/DetailsScreen';

// Create a stack navigator using createStackNavigator()
const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Home">
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Home' }} // Title for the header bar
        />
        <Stack.Screen
          name="Details"
          component={DetailsScreen}
          options={{ title: 'More Details' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}