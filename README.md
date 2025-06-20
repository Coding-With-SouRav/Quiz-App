# Quiz APP

1. **Multi-Theme Support**:
   - 5 color themes (Light, Dark, Blue, Green, Purple)
   - Theme persistence using JSON storage
   - Dynamic UI color updates

2. **Question System**:
   - 4 difficulty levels (Easy, Medium, Hard, Googly)
   - 100 auto-generated questions per category using Faker library
   - OpenTDB API integration for online questions
   - Internet availability detection

3. **Special Game Mechanics**:
   - "Googly Rounds" (double points) every 5 normal questions
   - Dynamic question sourcing (local cache + online API)

4. **User Interface**:
   - Clean Tkinter-based GUI with responsive layout
   - Question navigation (Previous/Next buttons)
   - Real-time score tracking
   - Option button coloring (green=correct, red=incorrect)

5. **Persistence Features**:
   - Window geometry saving/restoring (maximized/normal state)
   - Hidden storage directory (`~/.quiz_app_config`)
   - Configuration file management

6. **Technical Implementation**:
   - PyInstaller resource path handling
   - Windows app ID registration for taskbar grouping
   - Question history tracking with answer review
   - Dynamic option shuffling
   - Proper encapsulation using OOP

7. **Navigation & Flow**:
   - Dedicated home screen
   - Quiz progression tracking
   - Round indicators (normal/googly status)
   - Question counters

8. **Error Handling**:
   - Graceful fallback for missing icons
   - Internet connection failure handling
   - File operation error catching

The application combines locally generated content with online API questions, features a theming system with persistent settings, and implements unique quiz mechanics like special "Googly" rounds for enhanced gameplay variety.

# Demo Images

![Screenshot 2025-06-20 091552](https://github.com/user-attachments/assets/c61fa01b-a6d7-4c3d-bc79-fd467b4719e0)
![Screenshot 2025-06-20 091624](https://github.com/user-attachments/assets/082a44d0-1f9f-4ad6-b564-633ebca5bc1f)
![Screenshot 2025-06-20 091644](https://github.com/user-attachments/assets/8a8c1195-9414-42e0-96f0-6fcd6f503e4f)
