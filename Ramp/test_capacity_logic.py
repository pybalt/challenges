#!/usr/bin/env python3

capacity = 100
used = 40
size = 60

new_used = used + size
remaining = capacity - used

print(f"Capacity: {capacity}")
print(f"Used: {used}")
print(f"Remaining: {remaining}")
print(f"File size: {size}")
print(f"New used if added: {new_used}")
print(f"\nCheck 1: new_used > capacity: {new_used > capacity}")
print(f"Check 2: new_used >= capacity: {new_used >= capacity}")
print(f"Check 3: remaining < size: {remaining < size}")
print(f"Check 4: remaining >= size: {remaining >= size}")

print(f"\nFor the test to FAIL (as expected):")
print(f"  We need: remaining < size = {remaining < size}")
print(f"  Which means: {remaining} < {size} = {remaining < size}")

print(f"\nSo the check should be: if remaining < size, fail")
print(f"Which is: if (capacity - used) < size, fail")
print(f"Which is: if capacity < used + size, fail")
print(f"Which is: if capacity < new_used, fail")
print(f"Which is: if new_used > capacity, fail")

print(f"\nBut new_used = {new_used}, capacity = {capacity}")
print(f"new_used > capacity = {new_used > capacity}")

print(f"\nWait, maybe the issue is that we should use >= instead of >?")
print(f"new_used >= capacity = {new_used >= capacity}")

