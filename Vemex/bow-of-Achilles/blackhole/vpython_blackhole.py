# First, let's create a simple VPython visualization
# Note: This requires installing vpython (pip install vpython)

try:
    from vpython import *
    
    # Create scene
    scene = canvas(title='First-Person Black Hole Visualization', 
                   width=1000, height=600, 
                   background=color.black)
    
    # Set up the camera for first-person view
    scene.camera.follow(None)  # Free camera movement
    
    # Create black hole
    black_hole = sphere(pos=vector(0,0,0), radius=1, color=color.black, emissive=True)
    
    # Create accretion disk
    disk_objects = []
    for i in range(20):
        radius = 2 + i * 0.2
        disk = ring(pos=vector(0,0,0), axis=vector(0,0,1), 
                   radius=radius, thickness=0.1, 
                   color=color.red if i < 10 else color.orange)
        disk_objects.append(disk)
    
    # Create stars in background
    stars = []
    for i in range(100):
        x = random.uniform(-20, 20)
        y = random.uniform(-20, 20)
        z = random.uniform(-20, 20)
        # Make sure stars aren't too close to black hole
        if x*x + y*y + z*z > 9:
            star = sphere(pos=vector(x,y,z), radius=0.05, color=color.white, emissive=True)
            stars.append(star)
    
    # Create observer (camera position)
    observer = sphere(pos=vector(10,0,0), radius=0.2, color=color.blue)
    
    # Create gravitational lensing effect
    lens_ring = ring(pos=vector(0,0,0), axis=vector(0,0,1), 
                    radius=5, thickness=0.1, 
                    color=color.cyan, opacity=0.5)
    
    # Add some lensed star images
    for i in range(10):
        angle = random.uniform(0, 2*pi)
        radius = 4.5
        x = radius * cos(angle)
        y = radius * sin(angle)
        z = random.uniform(-0.5, 0.5)
        lensed_star = sphere(pos=vector(x,y,z), radius=0.1, color=color.cyan, emissive=True)
    
    # Add information text
    info = label(pos=vector(0,8,0), text='First-Person View Near Black Hole\nUse mouse to rotate view', 
                 xoffset=20, yoffset=50, space=30,
                 height=12, border=4, font='sans')
    
    # Animation loop
    t = 0
    dt = 0.01
    
    while True:
        rate(100)
        t += dt
        
        # Make the accretion disk rotate
        for i, disk in enumerate(disk_objects):
            disk.rotate(angle=dt * (0.5 + i*0.05), axis=vector(0,0,1))
        
        # Make some stars twinkle
        for star in stars[::10]:  # Every 10th star
            if random.random() < 0.02:
                star.color = vector(random.random(), random.random(), random.random())
    
    print("VPython visualization created successfully!")
    
except ImportError:
    print("VPython not installed. Creating alternative 3D visualization...")
    
    # Fallback to matplotlib 3D
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    
    # Create figure
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create black hole
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x_bh = np.outer(np.cos(u), np.sin(v))
    y_bh = np.outer(np.sin(u), np.sin(v))
    z_bh = np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x_bh, y_bh, z_bh, color='black', alpha=0.9)
    
    # Create accretion disk
    for i in range(10):
        radius = 1.5 + i * 0.3
        theta = np.linspace(0, 2*np.pi, 50)
        x_disk = radius * np.cos(theta)
        y_disk = radius * np.sin(theta)
        z_disk = np.zeros_like(theta)
        color_val = 0.5 + i * 0.05
        ax.plot(x_disk, y_disk, z_disk, color=(1, color_val, 0), alpha=0.7)
    
    # Create stars
    np.random.seed(42)  # For reproducible results
    star_x = np.random.uniform(-10, 10, 50)
    star_y = np.random.uniform(-10, 10, 50)
    star_z = np.random.uniform(-5, 5, 50)
    ax.scatter(star_x, star_y, star_z, c='white', s=5, alpha=0.8)
    
    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('3D Black Hole Visualization (Fallback Mode)')
    
    plt.show()
    
    print("Fallback matplotlib visualization created.")