class UserModel {
  final String id;
  final String email;
  final String fullName;
  final String targetRole;
  final String experienceLevel;
  final List<String> programmingLanguages;
  final String? phoneNumber;
  final String? profilePicture;
  final String country;
  final String timeZone;

  UserModel({
    required this.id,
    required this.email,
    required this.fullName,
    required this.targetRole,
    required this.experienceLevel,
    required this.programmingLanguages,
    this.phoneNumber,
    this.profilePicture,
    this.country = 'India (IST +5:30)',
    this.timeZone = 'Asia/Kolkata',
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id']?.toString() ?? 'usr-local',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? json['name'] ?? 'Candidate',
      targetRole: json['target_role'] ?? 'Full-Stack Developer',
      experienceLevel: json['experience_level'] ?? '3-5 Years',
      programmingLanguages: List<String>.from(json['programming_languages'] ?? []),
      phoneNumber: json['phone_number'],
      profilePicture: json['profile_picture'],
      country: json['country'] ?? 'India (IST +5:30)',
      timeZone: json['time_zone'] ?? 'Asia/Kolkata',
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'full_name': fullName,
        'target_role': targetRole,
        'experience_level': experienceLevel,
        'programming_languages': programmingLanguages,
        'phone_number': phoneNumber,
        'profile_picture': profilePicture,
        'country': country,
        'time_zone': timeZone,
      };

  UserModel copyWith({
    String? id,
    String? email,
    String? fullName,
    String? targetRole,
    String? experienceLevel,
    List<String>? programmingLanguages,
    String? phoneNumber,
    String? profilePicture,
    String? country,
    String? timeZone,
  }) {
    return UserModel(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      targetRole: targetRole ?? this.targetRole,
      experienceLevel: experienceLevel ?? this.experienceLevel,
      programmingLanguages: programmingLanguages ?? this.programmingLanguages,
      phoneNumber: phoneNumber ?? this.phoneNumber,
      profilePicture: profilePicture ?? this.profilePicture,
      country: country ?? this.country,
      timeZone: timeZone ?? this.timeZone,
    );
  }
}
